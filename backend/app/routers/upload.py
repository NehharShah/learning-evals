"""
Upload router for handling file uploads
Supports CSV and JSONL files with validation and parsing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging
from typing import List

from app.config import settings
from app.models import UploadResponse, PromptData, ErrorResponse
from app.utils.file_processing import (
    validate_file_size,
    validate_file_type,
    process_uploaded_file
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiter for upload endpoint
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request - validation error"},
        413: {"model": ErrorResponse, "description": "File too large"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Upload dataset file",
    description="Upload a CSV or JSONL file containing prompts and expected outputs for evaluation"
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def upload_dataset(
    request: Request,
    file: UploadFile = File(
        ...,
        description="CSV or JSONL file containing prompts and expected outputs",
        example="dataset.csv"
    )
):
    """
    Upload and parse a dataset file for LLM evaluation
    
    The file should contain:
    - **prompt/question/input**: The input prompt for the LLM
    - **expected_output/expected/answer**: The expected response
    
    **Supported formats:**
    - CSV: Comma-separated values with headers
    - JSONL: JSON Lines format (one JSON object per line)
    
    **File requirements:**
    - Maximum size: 5MB
    - Encoding: UTF-8 or Latin-1
    - Must contain valid prompt and expected output columns
    
    **Example CSV:**
    ```
    prompt,expected_output
    "What is the capital of France?","Paris"
    "Explain quantum computing","Quantum computing uses quantum mechanics principles"
    ```
    
    **Example JSONL:**
    ```
    {"prompt": "What is the capital of France?", "expected_output": "Paris"}
    {"prompt": "Explain quantum computing", "expected_output": "Quantum computing uses quantum mechanics principles"}
    ```
    """
    logger.info(f"Processing file upload: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        validate_file_type(file.filename, settings.ALLOWED_FILE_TYPES)
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        validate_file_size(len(content), settings.MAX_FILE_SIZE_BYTES)
        
        # Process the file
        processed_data, warnings = process_uploaded_file(content, file.filename)
        
        # Convert to PromptData objects for validation
        prompt_objects = []
        for item in processed_data:
            try:
                prompt_obj = PromptData(
                    prompt=item["prompt"],
                    expected_output=item["expected_output"],
                    metadata=item.get("metadata")
                )
                prompt_objects.append(prompt_obj)
            except Exception as e:
                logger.error(f"Failed to create PromptData object: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid data format: {str(e)}"
                )
        
        # Create preview (first 5 items)
        preview = prompt_objects[:5]
        
        # Build success response
        response = UploadResponse(
            success=True,
            message=f"Successfully uploaded and parsed {len(prompt_objects)} prompts",
            data=prompt_objects,
            total_prompts=len(prompt_objects),
            preview=preview
        )
        
        # Add warnings to response message if any
        if warnings:
            warning_text = ". Warnings: " + "; ".join(warnings)
            response.message += warning_text
        
        logger.info(f"Successfully processed {file.filename}: {len(prompt_objects)} prompts")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are expected)
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing file"
        )
    finally:
        # Clean up file handle
        await file.close()


@router.get(
    "/upload/info",
    summary="Get upload requirements",
    description="Get information about file upload requirements and supported formats"
)
async def get_upload_info():
    """
    Get information about file upload requirements
    
    Returns details about:
    - Supported file formats
    - Maximum file size
    - Required columns
    - Example formats
    """
    return {
        "supported_formats": settings.ALLOWED_FILE_TYPES,
        "max_file_size_mb": settings.max_file_size_mb,
        "max_file_size_bytes": settings.MAX_FILE_SIZE_BYTES,
        "required_columns": {
            "prompt_fields": ["prompt", "question", "input", "query"],
            "expected_output_fields": ["expected_output", "expected", "answer", "output", "target", "ground_truth"]
        },
        "examples": {
            "csv": {
                "format": "CSV with headers",
                "example": "prompt,expected_output\n\"What is the capital of France?\",\"Paris\""
            },
            "jsonl": {
                "format": "JSON Lines (one JSON object per line)",
                "example": "{\"prompt\": \"What is the capital of France?\", \"expected_output\": \"Paris\"}"
            }
        },
        "notes": [
            "Files must be UTF-8 or Latin-1 encoded",
            "Empty rows will be filtered out automatically",
            "Column names are case-insensitive",
            "Additional columns will be preserved as metadata"
        ]
    } 