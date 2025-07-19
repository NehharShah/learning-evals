"""
Configuration module for LLM Evaluation Tool backend
Uses Pydantic settings for environment variable management
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Multi-Provider Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    groq_api_key: Optional[str] = Field(None, env="GROQ_API_KEY")
    
    # Custom Provider Configuration
    custom_provider_url: Optional[str] = Field(None, env="CUSTOM_PROVIDER_URL")
    custom_provider_api_key: Optional[str] = Field(None, env="CUSTOM_PROVIDER_API_KEY")
    
    # Application Settings
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    
    # Security Settings
    secret_key: str = Field("dev-secret-key-change-in-production", env="SECRET_KEY")
    max_file_size_mb: int = Field(5, env="MAX_FILE_SIZE_MB")
    allowed_file_types: str = Field(".csv,.jsonl", env="ALLOWED_FILE_TYPES")
    
    # CORS Settings
    allowed_origins: str = Field(
        "http://localhost:3000,http://127.0.0.1:3000", 
        env="ALLOWED_ORIGINS"
    )
    
    # Trusted hosts for production
    allowed_hosts: str = Field("localhost,127.0.0.1", env="ALLOWED_HOSTS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    evaluation_rate_limit_per_minute: int = Field(10, env="EVALUATION_RATE_LIMIT_PER_MINUTE")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")
    
    # Model Defaults
    default_model: str = Field("gpt-3.5-turbo", env="DEFAULT_MODEL")
    enabled_providers: str = Field("openai", env="ENABLED_PROVIDERS")  # comma-separated list
    max_tokens: int = Field(1000, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    top_p: float = Field(1.0, env="TOP_P")
    frequency_penalty: float = Field(0.0, env="FREQUENCY_PENALTY")
    
    # Security Detection
    injection_keywords: str = Field(
        "ignore previous,disregard instructions,act as,pretend to be,forget everything,new instructions",
        env="INJECTION_KEYWORDS"
    )
    enable_toxicity_detection: bool = Field(False, env="ENABLE_TOXICITY_DETECTION")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("allowed_origins")
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("allowed_hosts")
    def parse_allowed_hosts(cls, v):
        """Parse comma-separated hosts into list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("allowed_file_types")
    def parse_allowed_file_types(cls, v):
        """Parse comma-separated file types into list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v
    
    @validator("injection_keywords")
    def parse_injection_keywords(cls, v):
        """Parse comma-separated keywords into list"""
        if isinstance(v, str):
            return [keyword.strip().lower() for keyword in v.split(",") if keyword.strip()]
        return v
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Get parsed allowed origins"""
        return self.allowed_origins
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Get parsed allowed hosts"""
        return self.allowed_hosts
    
    @property
    def ALLOWED_FILE_TYPES(self) -> List[str]:
        """Get parsed allowed file types"""
        return self.allowed_file_types
    
    @property
    def INJECTION_KEYWORDS(self) -> List[str]:
        """Get parsed injection keywords"""
        return self.injection_keywords
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024


# Create global settings instance
settings = Settings() 