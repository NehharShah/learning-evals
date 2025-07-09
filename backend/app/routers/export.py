"""
Export router for downloading evaluation results
Supports CSV and JSON export formats with flexible data selection
"""

import csv
import json
import io
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging

from app.config import settings
from app.models import (
    ExportRequest,
    ExportResponse,
    ExportFormat,
    EvaluationResult,
    ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiter for export endpoints
limiter = Limiter(key_func=get_remote_address)

# Import the results store from evaluation router
# In a real application, this would be a database
from app.routers.evaluation import evaluation_results_store


def generate_csv_content(results: List[EvaluationResult], include_metadata: bool = True) -> str:
    """
    Generate CSV content from evaluation results
    
    Args:
        results: List of evaluation results
        include_metadata: Whether to include metadata columns
        
    Returns:
        CSV content as string
    """
    if not results:
        return "No data available"
    
    # Define standard columns
    columns = [
        "ID",
        "Prompt",
        "Model Response",
        "Expected Output",
        "Exact Match (%)",
        "Fuzzy Match (%)",
        "Toxicity",
        "Model",
        "Timestamp"
    ]
    
    if include_metadata:
        columns.extend([
            "Security Flags",
            "Temperature",
            "Max Tokens",
            "Top P",
            "Frequency Penalty"
        ])
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(columns)
    
    # Write data rows
    for result in results:
        row = [
            result.id,
            result.prompt,
            result.model_response,
            result.expected_output,
            result.exact_match,
            result.fuzzy_match,
            "Yes" if result.toxicity else "No",
            result.model,
            result.timestamp
        ]
        
        if include_metadata:
            # Security flags
            security_flags = ", ".join(result.security_flags) if result.security_flags else "None"
            row.append(security_flags)
            
            # Model parameters
            if result.parameters:
                row.extend([
                    result.parameters.temperature,
                    result.parameters.max_tokens,
                    result.parameters.top_p,
                    result.parameters.frequency_penalty
                ])
            else:
                row.extend(["N/A", "N/A", "N/A", "N/A"])
        
        writer.writerow(row)
    
    return output.getvalue()


def generate_json_content(results: List[EvaluationResult], include_metadata: bool = True) -> str:
    """
    Generate JSON content from evaluation results
    
    Args:
        results: List of evaluation results
        include_metadata: Whether to include metadata
        
    Returns:
        JSON content as string
    """
    if not results:
        return json.dumps({"results": [], "message": "No data available"})
    
    # Convert results to dictionaries
    json_results = []
    for result in results:
        result_dict = {
            "id": result.id,
            "prompt": result.prompt,
            "model_response": result.model_response,
            "expected_output": result.expected_output,
            "exact_match": result.exact_match,
            "fuzzy_match": result.fuzzy_match,
            "toxicity": result.toxicity,
            "model": result.model,
            "timestamp": result.timestamp
        }
        
        if include_metadata:
            if result.security_flags:
                result_dict["security_flags"] = result.security_flags
            
            if result.parameters:
                result_dict["parameters"] = {
                    "temperature": result.parameters.temperature,
                    "max_tokens": result.parameters.max_tokens,
                    "top_p": result.parameters.top_p,
                    "frequency_penalty": result.parameters.frequency_penalty
                }
        
        json_results.append(result_dict)
    
    # Create export metadata
    export_data = {
        "export_info": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_results": len(results),
            "format": "json",
            "include_metadata": include_metadata
        },
        "results": json_results
    }
    
    return json.dumps(export_data, indent=2, default=str)


@router.post(
    "/export",
    responses={
        200: {"description": "File download", "content": {"application/octet-stream": {}}},
        400: {"model": ErrorResponse, "description": "Bad request - validation error"},
        404: {"model": ErrorResponse, "description": "No data to export"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Export evaluation results",
    description="Export evaluation results to CSV or JSON format for download"
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def export_results(
    request: Request,
    export_request: ExportRequest
):
    """
    Export evaluation results to the specified format
    
    **Supported formats:**
    - **CSV**: Comma-separated values with headers
    - **JSON**: Structured JSON with metadata
    
    **Options:**
    - Include/exclude metadata (parameters, security flags)
    - Export specific results or all available results
    
    **CSV format includes:**
    - All evaluation metrics and scores
    - Model parameters (if metadata enabled)
    - Security analysis results
    - Timestamps and identifiers
    
    **JSON format includes:**
    - Structured data with export metadata
    - All fields from CSV plus nested objects
    - Better preservation of data types
    """
    logger.info(f"Export request: format={export_request.format}, include_metadata={export_request.include_metadata}")
    
    try:
        # Determine which results to export
        if export_request.results:
            # Export specific results provided in request
            results = export_request.results
            logger.info(f"Exporting {len(results)} specific results")
        else:
            # Export all available results from store
            all_results = []
            for evaluation_results in evaluation_results_store.values():
                all_results.extend(evaluation_results)
            
            if not all_results:
                raise HTTPException(
                    status_code=404,
                    detail="No evaluation results available for export"
                )
            
            results = all_results
            logger.info(f"Exporting all {len(results)} available results")
        
        # Generate content based on format
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if export_request.format == ExportFormat.CSV:
            content = generate_csv_content(results, export_request.include_metadata)
            filename = f"llm_evaluation_results_{timestamp}.csv"
            media_type = "text/csv"
        else:  # JSON
            content = generate_json_content(results, export_request.include_metadata)
            filename = f"llm_evaluation_results_{timestamp}.json"
            media_type = "application/json"
        
        # Create streaming response for download
        def iter_content():
            yield content.encode('utf-8')
        
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": media_type,
        }
        
        logger.info(f"Generated export file: {filename} ({len(content)} bytes)")
        
        return StreamingResponse(
            iter_content(),
            media_type=media_type,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during export"
        )


@router.get(
    "/export/{evaluation_id}",
    responses={
        200: {"description": "File download", "content": {"application/octet-stream": {}}},
        404: {"model": ErrorResponse, "description": "Evaluation not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Export specific evaluation results",
    description="Export results from a specific evaluation by ID"
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def export_evaluation_results(
    request: Request,
    evaluation_id: str,
    format: ExportFormat = Query(ExportFormat.CSV, description="Export format"),
    include_metadata: bool = Query(True, description="Include metadata in export")
):
    """
    Export results from a specific evaluation
    
    This endpoint allows you to export results from a particular evaluation
    session by providing the evaluation ID.
    """
    logger.info(f"Export request for evaluation {evaluation_id}: format={format}")
    
    if evaluation_id not in evaluation_results_store:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation {evaluation_id} not found"
        )
    
    results = evaluation_results_store[evaluation_id]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    try:
        if format == ExportFormat.CSV:
            content = generate_csv_content(results, include_metadata)
            filename = f"evaluation_{evaluation_id}_{timestamp}.csv"
            media_type = "text/csv"
        else:  # JSON
            content = generate_json_content(results, include_metadata)
            filename = f"evaluation_{evaluation_id}_{timestamp}.json"
            media_type = "application/json"
        
        def iter_content():
            yield content.encode('utf-8')
        
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": media_type,
        }
        
        logger.info(f"Exported evaluation {evaluation_id}: {filename} ({len(content)} bytes)")
        
        return StreamingResponse(
            iter_content(),
            media_type=media_type,
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Export error for evaluation {evaluation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during export"
        )


@router.get(
    "/export/formats",
    summary="Get supported export formats",
    description="Get information about supported export formats and their features"
)
async def get_export_formats():
    """
    Get information about supported export formats
    
    Returns details about available formats, their features, and use cases.
    """
    return {
        "formats": [
            {
                "id": "csv",
                "name": "CSV (Comma-Separated Values)",
                "description": "Spreadsheet-compatible format",
                "media_type": "text/csv",
                "features": [
                    "Compatible with Excel, Google Sheets",
                    "Flat data structure",
                    "Easy to import into analysis tools",
                    "Human-readable"
                ],
                "use_cases": [
                    "Data analysis",
                    "Sharing with non-technical users",
                    "Import into BI tools"
                ]
            },
            {
                "id": "json",
                "name": "JSON (JavaScript Object Notation)",
                "description": "Structured data format",
                "media_type": "application/json",
                "features": [
                    "Preserves data types",
                    "Nested object support",
                    "Machine-readable",
                    "Includes export metadata"
                ],
                "use_cases": [
                    "API integration",
                    "Further processing",
                    "Backup and archival"
                ]
            }
        ],
        "options": {
            "include_metadata": {
                "description": "Include model parameters and security analysis",
                "default": True,
                "affects": ["CSV columns", "JSON structure"]
            }
        },
        "limits": {
            "max_results_per_export": 10000,
            "rate_limit_per_minute": settings.rate_limit_per_minute
        }
    }


@router.get(
    "/export/summary",
    summary="Get export summary",
    description="Get summary of available data for export"
)
async def get_export_summary():
    """
    Get summary of data available for export
    
    Returns information about:
    - Total number of results available
    - Number of evaluations
    - Date ranges
    - Models evaluated
    """
    all_results = []
    evaluations_count = len(evaluation_results_store)
    
    for evaluation_results in evaluation_results_store.values():
        all_results.extend(evaluation_results)
    
    if not all_results:
        return {
            "total_results": 0,
            "total_evaluations": 0,
            "date_range": None,
            "models": [],
            "summary": "No data available for export"
        }
    
    # Calculate summary statistics
    timestamps = [result.timestamp for result in all_results]
    models = list(set(result.model for result in all_results))
    
    # Find date range
    sorted_timestamps = sorted(timestamps)
    earliest = sorted_timestamps[0] if sorted_timestamps else None
    latest = sorted_timestamps[-1] if sorted_timestamps else None
    
    return {
        "total_results": len(all_results),
        "total_evaluations": evaluations_count,
        "date_range": {
            "earliest": earliest,
            "latest": latest
        } if earliest and latest else None,
        "models": models,
        "average_scores": {
            "exact_match": sum(r.exact_match for r in all_results) / len(all_results),
            "fuzzy_match": sum(r.fuzzy_match for r in all_results) / len(all_results)
        },
        "security_analysis": {
            "flagged_results": len([r for r in all_results if r.security_flags]),
            "toxic_results": len([r for r in all_results if r.toxicity])
        }
    } 