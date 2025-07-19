"""
Evaluation utilities for LLM performance assessment
Includes scoring, OpenAI API integration, and analysis functions
"""

import asyncio
import time
from typing import List, Dict, Any, Tuple, Optional
import logging
from datetime import datetime
import re

import openai
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein

from app.config import settings
from app.models import (
    PromptData, 
    EvaluationResult, 
    ModelParameters, 
    SecurityAnalysis, 
    SecurityAlert,
    AdvancedMetrics,
    ModelInfo
)
from .advanced_metrics import calculate_advanced_metrics
from .providers import (
    provider_manager, 
    OpenAIProvider, 
    AnthropicProvider, 
    GoogleProvider, 
    GroqProvider, 
    CustomProvider,
    ProviderConfig
)

logger = logging.getLogger(__name__)

# Initialize providers based on configuration
def initialize_providers():
    """Initialize available providers based on configuration"""
    enabled_providers = [p.strip() for p in settings.enabled_providers.split(",")]
    
    # Initialize OpenAI provider
    if "openai" in enabled_providers and settings.openai_api_key:
        try:
            openai_config = ProviderConfig(
                name="openai",
                api_key=settings.openai_api_key,
                timeout=30
            )
            openai_provider = OpenAIProvider(openai_config)
            provider_manager.add_provider("openai", openai_provider)
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {e}")
    
    # Initialize Anthropic provider
    if "anthropic" in enabled_providers and settings.anthropic_api_key:
        try:
            anthropic_config = ProviderConfig(
                name="anthropic",
                api_key=settings.anthropic_api_key,
                timeout=30
            )
            anthropic_provider = AnthropicProvider(anthropic_config)
            provider_manager.add_provider("anthropic", anthropic_provider)
            logger.info("Anthropic provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic provider: {e}")
    
    # Initialize Google provider
    if "google" in enabled_providers and settings.google_api_key:
        try:
            google_config = ProviderConfig(
                name="google",
                api_key=settings.google_api_key,
                timeout=30
            )
            google_provider = GoogleProvider(google_config)
            provider_manager.add_provider("google", google_provider)
            logger.info("Google provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Google provider: {e}")
    
    # Initialize Groq provider
    if "groq" in enabled_providers and settings.groq_api_key:
        try:
            groq_config = ProviderConfig(
                name="groq",
                api_key=settings.groq_api_key,
                timeout=30
            )
            groq_provider = GroqProvider(groq_config)
            provider_manager.add_provider("groq", groq_provider)
            logger.info("Groq provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Groq provider: {e}")
    
    # Initialize custom provider
    if "custom" in enabled_providers and settings.custom_provider_api_key and settings.custom_provider_url:
        try:
            custom_config = ProviderConfig(
                name="custom",
                api_key=settings.custom_provider_api_key,
                base_url=settings.custom_provider_url,
                timeout=30
            )
            custom_provider = CustomProvider(custom_config)
            provider_manager.add_provider("custom", custom_provider)
            logger.info("Custom provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize custom provider: {e}")
    
    logger.info(f"Initialized {len(provider_manager.providers)} providers")

# Initialize providers on module import
initialize_providers()


class EvaluationError(Exception):
    """Custom exception for evaluation errors"""
    pass


def calculate_exact_match(response: str, expected: str) -> float:
    """
    Calculate exact match score as percentage
    
    Args:
        response: Model's response
        expected: Expected output
        
    Returns:
        Exact match score (0-100)
    """
    if not response or not expected:
        return 0.0
    
    # Normalize strings: strip whitespace, convert to lowercase
    normalized_response = response.strip().lower()
    normalized_expected = expected.strip().lower()
    
    # Calculate exact match
    if normalized_response == normalized_expected:
        return 100.0
    else:
        return 0.0


def calculate_fuzzy_match(response: str, expected: str) -> float:
    """
    Calculate fuzzy match score using multiple algorithms
    
    Args:
        response: Model's response
        expected: Expected output
        
    Returns:
        Fuzzy match score (0-100)
    """
    if not response or not expected:
        return 0.0
    
    # Normalize strings
    response = response.strip()
    expected = expected.strip()
    
    if not response or not expected:
        return 0.0
    
    # Calculate different similarity scores
    scores = []
    
    # 1. Token sort ratio (good for word order differences)
    token_sort_score = fuzz.token_sort_ratio(response, expected)
    scores.append(token_sort_score)
    
    # 2. Token set ratio (good for subset matching)
    token_set_score = fuzz.token_set_ratio(response, expected)
    scores.append(token_set_score)
    
    # 3. Partial ratio (good for substring matching)
    partial_score = fuzz.partial_ratio(response, expected)
    scores.append(partial_score)
    
    # 4. Simple ratio (basic edit distance)
    simple_score = fuzz.ratio(response, expected)
    scores.append(simple_score)
    
    # Return the maximum score (most generous matching)
    return float(max(scores))


def detect_prompt_injection(prompt: str) -> SecurityAnalysis:
    """
    Detect potential prompt injection attempts
    
    Args:
        prompt: Input prompt to analyze
        
    Returns:
        Security analysis with alerts and score
    """
    alerts = []
    detected_patterns = []
    
    # Convert to lowercase for pattern matching
    prompt_lower = prompt.lower()
    
    # Check for injection keywords
    for keyword in settings.INJECTION_KEYWORDS:
        if keyword.lower() in prompt_lower:
            detected_patterns.append(keyword)
    
    # Additional pattern checks
    injection_patterns = [
        (r"ignore\s+(?:previous|earlier|all)\s+(?:instructions?|prompts?|commands?)", "ignore_instructions"),
        (r"forget\s+(?:everything|all|previous)", "forget_command"),
        (r"act\s+as\s+(?:a\s+)?(?:different|new|another)", "role_change"),
        (r"pretend\s+(?:to\s+be|you\s+are)", "pretend_command"),
        (r"disregard\s+(?:all|previous|the)", "disregard_command"),
        (r"override\s+(?:security|safety|instructions)", "override_command"),
        (r"sudo\s+mode", "sudo_command"),
        (r"developer\s+mode", "developer_mode"),
        (r"jailbreak", "jailbreak_attempt"),
    ]
    
    for pattern, alert_type in injection_patterns:
        if re.search(pattern, prompt_lower):
            detected_patterns.append(alert_type)
    
    # Create security alerts
    if detected_patterns:
        # High severity if multiple patterns detected
        severity = "high" if len(detected_patterns) > 2 else "medium"
        
        alert = SecurityAlert(
            type="prompt_injection",
            severity=severity,
            message=f"Potential prompt injection detected: {', '.join(detected_patterns)}",
            detected_patterns=detected_patterns
        )
        alerts.append(alert)
    
    # Calculate security score (0-100, higher is safer)
    base_score = 100.0
    penalty_per_pattern = 15.0
    
    security_score = max(0.0, base_score - (len(detected_patterns) * penalty_per_pattern))
    
    return SecurityAnalysis(
        is_suspicious=bool(detected_patterns),
        alerts=alerts,
        score=security_score
    )


def detect_toxicity(text: str) -> bool:
    """
    Placeholder for toxicity detection
    
    Args:
        text: Text to analyze for toxicity
        
    Returns:
        Whether text is considered toxic
    """
    # Placeholder implementation
    # In production, this would use a proper toxicity detection model
    # like Perspective API, Detoxify, or similar
    
    if not settings.enable_toxicity_detection:
        return False
    
    # Simple keyword-based detection for demonstration
    toxic_keywords = [
        "hate", "kill", "violence", "harmful", "dangerous",
        "offensive", "inappropriate", "toxic", "abusive"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in toxic_keywords)


async def call_llm_api(
    prompt: str, 
    model: str, 
    parameters: Optional[ModelParameters] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Call LLM API with the given prompt and parameters using the appropriate provider
    
    Args:
        prompt: Input prompt
        model: Model name (e.g., 'gpt-3.5-turbo', 'claude-3-sonnet-20240229')
        parameters: Model parameters
        
    Returns:
        Tuple of (response_text, metadata)
        
    Raises:
        EvaluationError: If API call fails
    """
    try:
        # Use default parameters if none provided
        if parameters is None:
            parameters = ModelParameters()
        
        # Convert parameters to dict for provider
        param_dict = parameters.dict(exclude_none=True)
        
        # Get the appropriate provider for the model
        provider = provider_manager.get_provider_for_model(model)
        if not provider:
            raise EvaluationError(f"No provider found for model: {model}")
        
        # Call the provider
        response_text, metadata = await provider.generate(prompt, model, param_dict)
        
        return response_text, metadata
        
    except Exception as e:
        logger.error(f"LLM API error for model {model}: {str(e)}")
        raise EvaluationError(f"API error: {str(e)}")


async def evaluate_single_prompt(
    prompt_data: PromptData,
    model: str,
    parameters: Optional[ModelParameters] = None,
    result_id: Optional[str] = None
) -> EvaluationResult:
    """
    Evaluate a single prompt against a model
    
    Args:
        prompt_data: Prompt and expected output data
        model: Model name to use
        parameters: Model parameters
        result_id: Optional custom ID for the result
        
    Returns:
        Evaluation result with scores and analysis
    """
    start_time = time.time()
    
    try:
        # Security analysis on the prompt
        security_analysis = detect_prompt_injection(prompt_data.prompt)
        
        # Call the model API
        model_response, api_metadata = await call_llm_api(
            prompt_data.prompt, 
            model, 
            parameters
        )
        
        # Calculate scores
        exact_match = calculate_exact_match(model_response, prompt_data.expected_output)
        fuzzy_match = calculate_fuzzy_match(model_response, prompt_data.expected_output)
        
        # Calculate advanced metrics
        advanced_metrics_data = calculate_advanced_metrics(prompt_data.expected_output, model_response)
        advanced_metrics = AdvancedMetrics(
            bleu_score=advanced_metrics_data["bleu_score"],
            rouge_scores=advanced_metrics_data["rouge_scores"],
            semantic_similarity=advanced_metrics_data["semantic_similarity"]
        )
        
        # Toxicity detection
        toxicity = detect_toxicity(model_response)
        
        # Security flags
        security_flags = []
        if security_analysis.is_suspicious:
            security_flags = [alert.type for alert in security_analysis.alerts]
        
        # Create result
        result = EvaluationResult(
            id=result_id or f"{int(time.time() * 1000000)}",
            prompt=prompt_data.prompt,
            model_response=model_response,
            expected_output=prompt_data.expected_output,
            exact_match=exact_match,
            fuzzy_match=fuzzy_match,
            toxicity=toxicity,
            model=model,
            provider=api_metadata.get("provider", "unknown"),
            timestamp=datetime.utcnow().isoformat(),
            parameters=parameters,
            security_flags=security_flags if security_flags else None,
            advanced_metrics=advanced_metrics
        )
        
        evaluation_time = time.time() - start_time
        logger.info(f"Evaluated prompt in {evaluation_time:.2f}s - exact: {exact_match:.1f}%, fuzzy: {fuzzy_match:.1f}%")
        
        return result
        
    except EvaluationError:
        raise
    except Exception as e:
        logger.error(f"Error evaluating prompt: {str(e)}")
        raise EvaluationError(f"Evaluation failed: {str(e)}")


async def evaluate_prompts_batch(
    prompts: List[PromptData],
    model: str,
    parameters: Optional[ModelParameters] = None,
    batch_size: int = 5,
    progress_callback: Optional[callable] = None
) -> List[EvaluationResult]:
    """
    Evaluate multiple prompts in batches with progress tracking
    
    Args:
        prompts: List of prompts to evaluate
        model: Model name to use
        parameters: Model parameters
        batch_size: Number of concurrent evaluations
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of evaluation results
    """
    results = []
    total_prompts = len(prompts)
    
    # Process in batches to avoid overwhelming the API
    for i in range(0, total_prompts, batch_size):
        batch = prompts[i:i + batch_size]
        
        # Create tasks for concurrent evaluation
        tasks = []
        for j, prompt_data in enumerate(batch):
            result_id = f"eval_{i + j + 1}"
            task = evaluate_single_prompt(prompt_data, model, parameters, result_id)
            tasks.append(task)
        
        # Execute batch concurrently
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Batch evaluation error: {str(result)}")
                # Create error result
                error_result = EvaluationResult(
                    id=f"error_{int(time.time() * 1000000)}",
                    prompt="Error processing prompt",
                    model_response=f"Error: {str(result)}",
                    expected_output="N/A",
                    exact_match=0.0,
                    fuzzy_match=0.0,
                    toxicity=False,
                    model=model,
                    timestamp=datetime.utcnow().isoformat(),
                    parameters=parameters
                )
                results.append(error_result)
            else:
                results.append(result)
        
        # Progress callback
        if progress_callback:
            progress = min(100.0, (len(results) / total_prompts) * 100)
            await progress_callback(len(results), total_prompts, progress)
        
        # Small delay between batches to be respectful to the API
        if i + batch_size < total_prompts:
            await asyncio.sleep(0.5)
    
    logger.info(f"Completed evaluation of {len(results)} prompts")
    return results 