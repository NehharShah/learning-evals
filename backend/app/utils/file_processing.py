"""
File processing utilities for handling CSV and JSONL uploads
Includes validation, parsing, and normalization functions
"""

import csv
import json
import io
from typing import List, Dict, Any, Tuple
import pandas as pd
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class FileProcessingError(Exception):
    """Custom exception for file processing errors"""
    pass


def validate_file_size(content_length: int, max_size_bytes: int) -> None:
    """
    Validate file size against maximum allowed size
    
    Args:
        content_length: Size of the file in bytes
        max_size_bytes: Maximum allowed size in bytes
        
    Raises:
        HTTPException: If file is too large
    """
    if content_length > max_size_bytes:
        max_size_mb = max_size_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size allowed: {max_size_mb:.1f}MB"
        )


def validate_file_type(filename: str, allowed_extensions: List[str]) -> None:
    """
    Validate file extension against allowed types
    
    Args:
        filename: Name of the uploaded file
        allowed_extensions: List of allowed file extensions (e.g., ['.csv', '.jsonl'])
        
    Raises:
        HTTPException: If file type is not allowed
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_extension = filename.lower()
    for ext in allowed_extensions:
        if file_extension.endswith(ext.lower()):
            return
    
    allowed_str = ", ".join(allowed_extensions)
    raise HTTPException(
        status_code=400,
        detail=f"Unsupported file type. Allowed types: {allowed_str}"
    )


def parse_csv_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse CSV content and return list of dictionaries
    
    Args:
        content: Raw CSV content as string
        
    Returns:
        List of dictionaries with parsed data
        
    Raises:
        FileProcessingError: If CSV parsing fails
    """
    try:
        # Use StringIO to treat string as file-like object
        csv_file = io.StringIO(content)
        
        # Try to detect delimiter
        sample = content[:1024]
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(sample).delimiter
        except csv.Error:
            delimiter = ','  # Default to comma
        
        # Read CSV
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        data = []
        for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
            # Filter out empty rows
            if not any(value.strip() for value in row.values() if value):
                continue
                
            # Clean up the row data
            cleaned_row = {}
            for key, value in row.items():
                if key is not None:  # Skip None keys
                    cleaned_key = key.strip().lower()
                    cleaned_value = value.strip() if value else ""
                    cleaned_row[cleaned_key] = cleaned_value
            
            if cleaned_row:  # Only add non-empty rows
                data.append(cleaned_row)
        
        if not data:
            raise FileProcessingError("CSV file is empty or contains no valid data")
        
        return data
        
    except csv.Error as e:
        raise FileProcessingError(f"Failed to parse CSV: {str(e)}")
    except Exception as e:
        raise FileProcessingError(f"Unexpected error parsing CSV: {str(e)}")


def parse_jsonl_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse JSONL content and return list of dictionaries
    
    Args:
        content: Raw JSONL content as string
        
    Returns:
        List of dictionaries with parsed data
        
    Raises:
        FileProcessingError: If JSONL parsing fails
    """
    try:
        data = []
        lines = content.strip().split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            try:
                parsed_line = json.loads(line)
                if isinstance(parsed_line, dict):
                    data.append(parsed_line)
                else:
                    logger.warning(f"Line {line_num} is not a JSON object, skipping")
            except json.JSONDecodeError as e:
                raise FileProcessingError(f"Invalid JSON on line {line_num}: {str(e)}")
        
        if not data:
            raise FileProcessingError("JSONL file is empty or contains no valid JSON objects")
        
        return data
        
    except Exception as e:
        if isinstance(e, FileProcessingError):
            raise
        raise FileProcessingError(f"Unexpected error parsing JSONL: {str(e)}")


def normalize_prompt_data(raw_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Normalize parsed data to standard prompt format
    
    Args:
        raw_data: List of dictionaries from parsed file
        
    Returns:
        Tuple of (normalized_data, warnings)
        
    Raises:
        FileProcessingError: If required fields are missing
    """
    normalized_data = []
    warnings = []
    
    # Common field mappings
    prompt_fields = ['prompt', 'question', 'input', 'query']
    expected_fields = ['expected_output', 'expected', 'answer', 'output', 'target', 'ground_truth']
    
    for i, row in enumerate(raw_data):
        # Convert all keys to lowercase for consistent matching
        row_lower = {k.lower(): v for k, v in row.items()}
        
        # Find prompt field
        prompt_value = None
        for field in prompt_fields:
            if field in row_lower and row_lower[field]:
                prompt_value = str(row_lower[field]).strip()
                break
        
        if not prompt_value:
            available_fields = list(row_lower.keys())
            raise FileProcessingError(
                f"Row {i+1}: No valid prompt field found. "
                f"Available fields: {available_fields}. "
                f"Expected one of: {prompt_fields}"
            )
        
        # Find expected output field
        expected_value = None
        for field in expected_fields:
            if field in row_lower and row_lower[field]:
                expected_value = str(row_lower[field]).strip()
                break
        
        if not expected_value:
            available_fields = list(row_lower.keys())
            raise FileProcessingError(
                f"Row {i+1}: No valid expected output field found. "
                f"Available fields: {available_fields}. "
                f"Expected one of: {expected_fields}"
            )
        
        # Create normalized entry
        normalized_entry = {
            "prompt": prompt_value,
            "expected_output": expected_value
        }
        
        # Add any additional metadata
        metadata = {}
        for key, value in row_lower.items():
            if key not in prompt_fields + expected_fields and value:
                metadata[key] = str(value)
        
        if metadata:
            normalized_entry["metadata"] = metadata
        
        normalized_data.append(normalized_entry)
    
    # Add warnings for common issues
    if len(normalized_data) != len(raw_data):
        warnings.append(f"Filtered out {len(raw_data) - len(normalized_data)} empty rows")
    
    return normalized_data, warnings


def process_uploaded_file(content: bytes, filename: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Main function to process uploaded file content
    
    Args:
        content: Raw file content as bytes
        filename: Name of the uploaded file
        
    Returns:
        Tuple of (processed_data, warnings)
        
    Raises:
        HTTPException: For various file processing errors
    """
    try:
        # Decode content to string
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content_str = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to decode file. Please ensure file is in UTF-8 or Latin-1 encoding"
                )
        
        # Parse based on file extension
        if filename.lower().endswith('.csv'):
            raw_data = parse_csv_content(content_str)
        elif filename.lower().endswith('.jsonl'):
            raw_data = parse_jsonl_content(content_str)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format"
            )
        
        # Normalize the data
        normalized_data, warnings = normalize_prompt_data(raw_data)
        
        logger.info(f"Successfully processed {filename}: {len(normalized_data)} prompts")
        
        return normalized_data, warnings
        
    except FileProcessingError as e:
        logger.error(f"File processing error for {filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal error processing file"
        ) 