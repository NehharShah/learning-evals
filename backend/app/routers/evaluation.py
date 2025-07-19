"""
Evaluation router for LLM performance assessment
Handles evaluation requests, progress tracking, and result generation
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging
from datetime import datetime

from app.config import settings
from app.models import (
    EvaluationRequest,
    EvaluationResponse,
    EvaluationResult,
    EvaluationSummary,
    AdvancedMetricsSummary,
    ErrorResponse,
    ModelParameters,
    PromptData
)
from app.utils.evaluation import (
    evaluate_prompts_batch,
    evaluate_single_prompt,
    EvaluationError
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiter for evaluation endpoints
limiter = Limiter(key_func=get_remote_address)

# In-memory storage for evaluation results (in production, use a database)
evaluation_results_store: Dict[str, List[EvaluationResult]] = {}
evaluation_status_store: Dict[str, Dict[str, Any]] = {}


def generate_summary(results: List[EvaluationResult]) -> EvaluationSummary:
    """
    Generate summary statistics from evaluation results
    
    Args:
        results: List of evaluation results
        
    Returns:
        Summary statistics
    """
    if not results:
        return EvaluationSummary(
            total_prompts=0,
            average_exact_match=0.0,
            average_fuzzy_match=0.0,
            flagged_prompts=0,
            security_score=100.0,
            models_used=[],
            evaluation_time=0.0,
            advanced_metrics_summary=None
        )
    
    total_prompts = len(results)
    
    # Calculate averages
    exact_scores = [r.exact_match for r in results]
    fuzzy_scores = [r.fuzzy_match for r in results]
    average_exact_match = sum(exact_scores) / total_prompts
    average_fuzzy_match = sum(fuzzy_scores) / total_prompts
    
    # Count flagged prompts (low scores or toxicity)
    flagged_prompts = len([
        r for r in results 
        if r.exact_match < 50 or r.toxicity or (r.security_flags and len(r.security_flags) > 0)
    ])
    
    # Calculate security score (average of individual security analyses)
    security_scores = []
    for result in results:
        if result.security_flags and len(result.security_flags) > 0:
            # Lower score for flagged content
            security_scores.append(max(0, 100 - len(result.security_flags) * 20))
        else:
            security_scores.append(100)
    
    security_score = sum(security_scores) / len(security_scores) if security_scores else 100.0
    
    # Get unique models used
    models_used = list(set(r.model for r in results))
    
    # Calculate advanced metrics summary
    advanced_metrics_summary = None
    if any(r.advanced_metrics for r in results):
        bleu_scores = [r.advanced_metrics.bleu_score for r in results if r.advanced_metrics]
        average_bleu_score = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
        
        # Calculate average ROUGE F1 scores
        rouge_f1_scores = {"rouge-1": [], "rouge-2": [], "rouge-l": []}
        for result in results:
            if result.advanced_metrics:
                for rouge_type in rouge_f1_scores:
                    if rouge_type in result.advanced_metrics.rouge_scores:
                        rouge_f1_scores[rouge_type].append(
                            result.advanced_metrics.rouge_scores[rouge_type]["f1"]
                        )
        
        average_rouge_f1 = {
            rouge_type: sum(scores) / len(scores) if scores else 0.0
            for rouge_type, scores in rouge_f1_scores.items()
        }
        
        # Calculate average semantic similarity scores
        semantic_scores = {"tfidf": [], "jaccard": [], "sequence": []}
        for result in results:
            if result.advanced_metrics:
                for method in semantic_scores:
                    if method in result.advanced_metrics.semantic_similarity:
                        semantic_scores[method].append(
                            result.advanced_metrics.semantic_similarity[method]
                        )
        
        average_semantic_similarity = {
            method: sum(scores) / len(scores) if scores else 0.0
            for method, scores in semantic_scores.items()
        }
        
        advanced_metrics_summary = AdvancedMetricsSummary(
            average_bleu_score=average_bleu_score,
            average_rouge_f1=average_rouge_f1,
            average_semantic_similarity=average_semantic_similarity
        )
    
    return EvaluationSummary(
        total_prompts=total_prompts,
        average_exact_match=average_exact_match,
        average_fuzzy_match=average_fuzzy_match,
        flagged_prompts=flagged_prompts,
        security_score=security_score,
        models_used=models_used,
        evaluation_time=0.0,  # Will be calculated by the endpoint
        advanced_metrics_summary=advanced_metrics_summary
    )


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request - validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Run LLM evaluation",
    description="Evaluate prompts against the selected LLM model and return detailed results"
)
@limiter.limit(f"{settings.evaluation_rate_limit_per_minute}/minute")
async def evaluate_prompts(
    request: Request,
    evaluation_request: EvaluationRequest
):
    """
    Evaluate a list of prompts against the specified LLM model
    
    **Process:**
    1. Validates the request and prompts
    2. Sends each prompt to the selected model via OpenAI API
    3. Calculates exact match and fuzzy match scores
    4. Performs security analysis for prompt injection
    5. Returns comprehensive evaluation results
    
    **Scoring:**
    - **Exact Match**: Binary score (0% or 100%) for exact string matching
    - **Fuzzy Match**: Similarity score (0-100%) using multiple algorithms:
      - Token sort ratio (handles word order differences)
      - Token set ratio (handles subset matching)
      - Partial ratio (handles substring matching)
      - Simple ratio (basic edit distance)
    
    **Security Features:**
    - Prompt injection detection using keyword and pattern analysis
    - Toxicity detection (placeholder implementation)
    - Security flags for suspicious content
    
    **Rate Limiting:**
    - Limited to {settings.evaluation_rate_limit_per_minute} requests per minute per IP
    - Batch processing for efficient API usage
    """
    start_time = time.time()
    evaluation_id = f"eval_{int(time.time() * 1000)}"
    
    logger.info(f"Starting evaluation {evaluation_id} with {len(evaluation_request.prompts)} prompts using {evaluation_request.model}")
    
    try:
        # Validate request
        if not evaluation_request.prompts:
            raise HTTPException(
                status_code=400,
                detail="No prompts provided for evaluation"
            )
        
        if len(evaluation_request.prompts) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 prompts allowed per evaluation"
            )
        
        # Initialize progress tracking
        evaluation_status_store[evaluation_id] = {
            "status": "running",
            "progress": 0,
            "total": len(evaluation_request.prompts),
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Progress callback for tracking
        async def progress_callback(current: int, total: int, percentage: float):
            evaluation_status_store[evaluation_id].update({
                "progress": current,
                "percentage": percentage,
                "status": "running"
            })
        
        # Run evaluation
        try:
            results = await evaluate_prompts_batch(
                evaluation_request.prompts,
                evaluation_request.model.value,
                evaluation_request.parameters,
                batch_size=5,  # Process 5 prompts concurrently
                progress_callback=progress_callback
            )
        except EvaluationError as e:
            logger.error(f"Evaluation error for {evaluation_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Calculate evaluation time
        evaluation_time = time.time() - start_time
        
        # Generate summary
        summary = generate_summary(results)
        summary.evaluation_time = evaluation_time
        
        # Store results for potential export
        evaluation_results_store[evaluation_id] = results
        
        # Update status
        evaluation_status_store[evaluation_id].update({
            "status": "completed",
            "progress": len(results),
            "percentage": 100.0,
            "completed_at": datetime.utcnow().isoformat(),
            "evaluation_time": evaluation_time
        })
        
        # Create response
        response = EvaluationResponse(
            success=True,
            message=f"Successfully evaluated {len(results)} prompts in {evaluation_time:.2f} seconds",
            results=results,
            total_evaluations=len(results),
            summary=summary.dict()
        )
        
        logger.info(f"Completed evaluation {evaluation_id}: {len(results)} results, avg exact: {summary.average_exact_match:.1f}%, avg fuzzy: {summary.average_fuzzy_match:.1f}%")
        
        return response
        
    except HTTPException:
        # Update status for HTTP errors
        evaluation_status_store[evaluation_id] = {
            "status": "failed",
            "error": "Validation or client error",
            "failed_at": datetime.utcnow().isoformat()
        }
        raise
    except Exception as e:
        logger.error(f"Unexpected error in evaluation {evaluation_id}: {str(e)}", exc_info=True)
        
        # Update status for unexpected errors
        evaluation_status_store[evaluation_id] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error during evaluation"
        )


@router.post(
    "/evaluate/single",
    response_model=EvaluationResult,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request - validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Evaluate single prompt",
    description="Evaluate a single prompt against the selected model for quick testing"
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def evaluate_single(
    request: Request,
    prompt: str,
    expected_output: str,
    model: str = "gpt-3.5-turbo",
    parameters: Optional[ModelParameters] = None
):
    """
    Evaluate a single prompt for quick testing and experimentation
    
    This endpoint is useful for:
    - Testing prompts before batch evaluation
    - Quick quality checks
    - Experimenting with different parameters
    """
    logger.info(f"Single evaluation request for model {model}")
    
    try:
        # Create prompt data
        prompt_data = PromptData(
            prompt=prompt,
            expected_output=expected_output
        )
        
        # Evaluate the prompt
        result = await evaluate_single_prompt(
            prompt_data,
            model,
            parameters or ModelParameters(),
            f"single_{int(time.time() * 1000000)}"
        )
        
        logger.info(f"Single evaluation completed: exact: {result.exact_match:.1f}%, fuzzy: {result.fuzzy_match:.1f}%")
        
        return result
        
    except EvaluationError as e:
        logger.error(f"Single evaluation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in single evaluation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during evaluation"
        )


@router.get(
    "/evaluate/status/{evaluation_id}",
    summary="Get evaluation status",
    description="Get the current status and progress of a running evaluation"
)
async def get_evaluation_status(evaluation_id: str):
    """
    Get the status and progress of an evaluation
    
    Returns information about:
    - Current progress (number completed / total)
    - Status (running, completed, failed)
    - Timestamps
    - Error information (if failed)
    """
    if evaluation_id not in evaluation_status_store:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )
    
    return evaluation_status_store[evaluation_id]


@router.get(
    "/evaluate/results/{evaluation_id}",
    response_model=List[EvaluationResult],
    summary="Get evaluation results",
    description="Retrieve the results of a completed evaluation"
)
async def get_evaluation_results(evaluation_id: str):
    """
    Get the full results of a completed evaluation
    
    This endpoint allows you to retrieve results from previous evaluations
    for analysis or export.
    """
    if evaluation_id not in evaluation_results_store:
        raise HTTPException(
            status_code=404,
            detail="Evaluation results not found"
        )
    
    return evaluation_results_store[evaluation_id]


@router.get(
    "/models",
    summary="Get available models",
    description="Get list of available LLM models for evaluation"
)
async def get_available_models():
    """
    Get information about available LLM models
    
    Returns details about supported models, their capabilities,
    and recommended use cases.
    """
    return {
        "models": [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "description": "Most capable model, best for complex reasoning",
                "max_tokens": 4000,
                "recommended_for": ["complex reasoning", "code generation", "analysis"]
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "description": "Fast and efficient, good for most tasks",
                "max_tokens": 4000,
                "recommended_for": ["general tasks", "conversation", "summarization"]
            },
            {
                "id": "gpt-4-turbo-preview",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "description": "Latest GPT-4 with improved performance",
                "max_tokens": 4000,
                "recommended_for": ["latest capabilities", "performance critical tasks"]
            },
            {
                "id": "claude-3",
                "name": "Claude 3",
                "provider": "Anthropic",
                "description": "Currently mapped to GPT-4 (integration pending)",
                "max_tokens": 4000,
                "note": "Full integration coming soon"
            },
            {
                "id": "gemini-pro",
                "name": "Gemini Pro",
                "provider": "Google",
                "description": "Currently mapped to GPT-3.5 (integration pending)",
                "max_tokens": 4000,
                "note": "Full integration coming soon"
            },
            {
                "id": "llama-2",
                "name": "Llama 2",
                "provider": "Meta",
                "description": "Currently mapped to GPT-3.5 (integration pending)",
                "max_tokens": 4000,
                "note": "Full integration coming soon"
            }
        ],
        "note": "Non-OpenAI models currently fallback to OpenAI models. Full multi-provider support coming soon."
    }


@router.delete(
    "/evaluate/results/{evaluation_id}",
    summary="Delete evaluation results",
    description="Delete stored evaluation results to free up memory"
)
async def delete_evaluation_results(evaluation_id: str):
    """
    Delete evaluation results and status information
    
    This helps clean up memory and remove old evaluation data.
    """
    deleted_items = []
    
    if evaluation_id in evaluation_results_store:
        del evaluation_results_store[evaluation_id]
        deleted_items.append("results")
    
    if evaluation_id in evaluation_status_store:
        del evaluation_status_store[evaluation_id]
        deleted_items.append("status")
    
    if not deleted_items:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )
    
    return {
        "success": True,
        "message": f"Deleted {', '.join(deleted_items)} for evaluation {evaluation_id}",
        "deleted_items": deleted_items
    } 