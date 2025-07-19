"""
Pydantic models for API requests and responses
Matches frontend data structures and expectations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class Provider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    CUSTOM = "custom"


class ModelName(str, Enum):
    """Available LLM models"""
    # OpenAI Models
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    
    # Anthropic Models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Google Models
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_PRO = "gemini-pro"
    
    # Groq Models
    LLAMA3_70B = "llama3-70b-8192"
    LLAMA3_8B = "llama3-8b-8192"
    MIXTRAL_8X7B = "mixtral-8x7b-32768"
    
    # Legacy mappings (for backward compatibility)
    CLAUDE_3 = "claude-3-sonnet-20240229"  # Map to Claude 3 Sonnet
    GEMINI_PRO_LEGACY = "gemini-pro"  # Map to Gemini Pro
    LLAMA_2 = "llama3-70b-8192"  # Map to Llama 3 70B


class ExportFormat(str, Enum):
    """Supported export formats"""
    CSV = "csv"
    JSON = "json"


# Upload Models
class PromptData(BaseModel):
    """Individual prompt data structure"""
    prompt: str = Field(..., description="The input prompt")
    expected_output: str = Field(..., description="Expected model response")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator("prompt", "expected_output")
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class UploadResponse(BaseModel):
    """Response for file upload endpoint"""
    success: bool = Field(..., description="Whether upload was successful")
    message: str = Field(..., description="Status message")
    data: List[PromptData] = Field(..., description="Parsed prompt data")
    total_prompts: int = Field(..., description="Total number of prompts")
    preview: List[PromptData] = Field(..., description="First 5 prompts for preview")


# Evaluation Models
class ModelParameters(BaseModel):
    """LLM model parameters"""
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Maximum tokens to generate")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    top_k: Optional[int] = Field(None, ge=1, le=100, description="Top-k sampling parameter (Google models)")
    presence_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="Presence penalty (OpenAI models)")


class ModelInfo(BaseModel):
    """Information about a model"""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Display name")
    provider: str = Field(..., description="Provider name")
    max_tokens: int = Field(..., description="Maximum tokens")
    context_length: Optional[int] = Field(None, description="Context length")
    description: Optional[str] = Field(None, description="Model description")
    capabilities: Optional[List[str]] = Field(None, description="Model capabilities")
    is_available: bool = Field(True, description="Whether model is available")


class EvaluationRequest(BaseModel):
    """Request for evaluation endpoint"""
    prompts: List[PromptData] = Field(..., description="List of prompts to evaluate")
    model: ModelName = Field(..., description="Selected model for evaluation")
    parameters: Optional[ModelParameters] = Field(None, description="Model parameters")
    
    @validator("prompts")
    def validate_prompts_not_empty(cls, v):
        if not v:
            raise ValueError("Prompts list cannot be empty")
        if len(v) > 100:  # Reasonable limit
            raise ValueError("Maximum 100 prompts per evaluation")
        return v


class AdvancedMetrics(BaseModel):
    """Advanced evaluation metrics"""
    bleu_score: float = Field(..., ge=0, le=1, description="BLEU score (0-1)", alias="bleuScore")
    rouge_scores: Dict[str, Dict[str, float]] = Field(..., description="ROUGE scores (precision, recall, f1)", alias="rougeScores")
    semantic_similarity: Dict[str, float] = Field(..., description="Semantic similarity scores", alias="semanticSimilarity")
    
    class Config:
        allow_population_by_field_name = True


class EvaluationResult(BaseModel):
    """Individual evaluation result"""
    id: Union[int, str] = Field(..., description="Unique result identifier")
    prompt: str = Field(..., description="Original prompt")
    model_response: str = Field(..., description="Model's response", alias="modelResponse")
    expected_output: str = Field(..., description="Expected output", alias="expectedOutput")
    exact_match: float = Field(..., ge=0, le=100, description="Exact match score (percentage)", alias="exactMatch")
    fuzzy_match: float = Field(..., ge=0, le=100, description="Fuzzy match score (percentage)", alias="fuzzyMatch")
    toxicity: bool = Field(..., description="Whether content is flagged as toxic")
    model: str = Field(..., description="Model used for evaluation")
    provider: Optional[str] = Field(None, description="Provider used for evaluation")
    timestamp: str = Field(..., description="ISO timestamp of evaluation")
    parameters: Optional[ModelParameters] = Field(None, description="Model parameters used")
    security_flags: Optional[List[str]] = Field(None, description="Security warnings", alias="securityFlags")
    advanced_metrics: Optional[AdvancedMetrics] = Field(None, description="Advanced evaluation metrics", alias="advancedMetrics")
    
    class Config:
        allow_population_by_field_name = True


class EvaluationResponse(BaseModel):
    """Response for evaluation endpoint"""
    success: bool = Field(..., description="Whether evaluation was successful")
    message: str = Field(..., description="Status message")
    results: List[EvaluationResult] = Field(..., description="Evaluation results")
    total_evaluations: int = Field(..., description="Total number of evaluations")
    summary: Dict[str, Any] = Field(..., description="Evaluation summary statistics")


class EvaluationProgress(BaseModel):
    """Real-time evaluation progress"""
    current: int = Field(..., description="Current evaluation number")
    total: int = Field(..., description="Total evaluations")
    percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    status: str = Field(..., description="Current status")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated seconds remaining")


# Export Models
class ExportRequest(BaseModel):
    """Request for export endpoint"""
    format: ExportFormat = Field(..., description="Export format")
    results: Optional[List[EvaluationResult]] = Field(None, description="Specific results to export")
    include_metadata: bool = Field(True, description="Whether to include metadata")


class ExportResponse(BaseModel):
    """Response for export endpoint"""
    success: bool = Field(..., description="Whether export was successful")
    message: str = Field(..., description="Status message")
    download_url: Optional[str] = Field(None, description="Download URL for the exported file")
    filename: str = Field(..., description="Generated filename")


# Security Models
class SecurityAlert(BaseModel):
    """Security alert for suspicious content"""
    type: str = Field(..., description="Type of security alert")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    message: str = Field(..., description="Alert message")
    detected_patterns: List[str] = Field(..., description="Detected suspicious patterns")


class SecurityAnalysis(BaseModel):
    """Security analysis result"""
    is_suspicious: bool = Field(..., description="Whether content is suspicious")
    alerts: List[SecurityAlert] = Field(..., description="List of security alerts")
    score: float = Field(..., ge=0, le=100, description="Security score (higher is safer)")


# Common Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")
    version: str = Field("1.0.0", description="API version")
    environment: str = Field(..., description="Environment name")


# Summary Statistics Models
class AdvancedMetricsSummary(BaseModel):
    """Summary of advanced metrics"""
    average_bleu_score: float = Field(..., ge=0, le=1, description="Average BLEU score", alias="averageBleuScore")
    average_rouge_f1: Dict[str, float] = Field(..., description="Average ROUGE F1 scores", alias="averageRougeF1")
    average_semantic_similarity: Dict[str, float] = Field(..., description="Average semantic similarity scores", alias="averageSemanticSimilarity")
    
    class Config:
        allow_population_by_field_name = True


class EvaluationSummary(BaseModel):
    """Summary statistics for evaluations"""
    total_prompts: int = Field(..., description="Total number of prompts evaluated")
    average_exact_match: float = Field(..., ge=0, le=100, description="Average exact match score")
    average_fuzzy_match: float = Field(..., ge=0, le=100, description="Average fuzzy match score")
    flagged_prompts: int = Field(..., description="Number of flagged prompts")
    security_score: float = Field(..., ge=0, le=100, description="Overall security score")
    models_used: List[str] = Field(..., description="List of models used")
    evaluation_time: float = Field(..., description="Total evaluation time in seconds")
    advanced_metrics_summary: Optional[AdvancedMetricsSummary] = Field(None, description="Summary of advanced metrics", alias="advancedMetricsSummary")


class ScoreDistribution(BaseModel):
    """Score distribution data for charts"""
    range: str = Field(..., description="Score range (e.g., '0-25%')")
    exact_match: int = Field(..., description="Count of exact matches in range")
    fuzzy_match: int = Field(..., description="Count of fuzzy matches in range") 