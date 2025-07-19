"""
Multi-provider LLM API integration
Supports OpenAI, Anthropic, Google, Groq, and custom providers
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx

# Provider-specific imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic library not available")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logging.warning("Google Generative AI library not available")

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    name: str
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


@dataclass
class ModelInfo:
    """Information about a model"""
    id: str
    name: str
    provider: str
    max_tokens: int
    context_length: Optional[int] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None


class BaseProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self):
        """Setup the provider's client"""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text from the model"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Validate if a model is supported by this provider"""
        pass


class OpenAIProvider(BaseProvider):
    """OpenAI API provider"""
    
    def _setup_client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        openai.api_key = self.config.api_key
        if self.config.base_url:
            openai.api_base = self.config.base_url
        self.client = openai
    
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using OpenAI API"""
        try:
            response = await self.client.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=parameters.get("max_tokens", 1000),
                temperature=parameters.get("temperature", 0.7),
                top_p=parameters.get("top_p", 1.0),
                frequency_penalty=parameters.get("frequency_penalty", 0.0),
                presence_penalty=parameters.get("presence_penalty", 0.0),
                timeout=self.config.timeout
            )
            
            response_text = response.choices[0].message.content.strip()
            metadata = {
                "model": model,
                "provider": "openai",
                "usage": response.usage.dict() if response.usage else {},
                "finish_reason": response.choices[0].finish_reason,
                "parameters": parameters
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available OpenAI models"""
        return [
            ModelInfo(
                id="gpt-4",
                name="GPT-4",
                provider="openai",
                max_tokens=4000,
                context_length=8192,
                description="Most capable model, best for complex reasoning",
                capabilities=["complex reasoning", "code generation", "analysis"]
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="openai",
                max_tokens=4000,
                context_length=4096,
                description="Fast and efficient, good for most tasks",
                capabilities=["general tasks", "conversation", "summarization"]
            ),
            ModelInfo(
                id="gpt-4-turbo-preview",
                name="GPT-4 Turbo",
                provider="openai",
                max_tokens=4000,
                context_length=128000,
                description="Latest GPT-4 with improved performance",
                capabilities=["latest capabilities", "performance critical tasks"]
            )
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate OpenAI model"""
        valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"]
        return model in valid_models


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider"""
    
    def _setup_client(self):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not available")
        
        self.client = anthropic.Anthropic(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using Anthropic API"""
        try:
            response = await self.client.messages.acreate(
                model=model,
                max_tokens=parameters.get("max_tokens", 1000),
                temperature=parameters.get("temperature", 0.7),
                top_p=parameters.get("top_p", 1.0),
                messages=[{"role": "user", "content": prompt}],
                timeout=self.config.timeout
            )
            
            response_text = response.content[0].text.strip()
            metadata = {
                "model": model,
                "provider": "anthropic",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "finish_reason": response.stop_reason,
                "parameters": parameters
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available Anthropic models"""
        return [
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider="anthropic",
                max_tokens=4000,
                context_length=200000,
                description="Most capable Claude model",
                capabilities=["complex reasoning", "analysis", "creative tasks"]
            ),
            ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider="anthropic",
                max_tokens=4000,
                context_length=200000,
                description="Balanced performance and speed",
                capabilities=["general tasks", "analysis", "writing"]
            ),
            ModelInfo(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                provider="anthropic",
                max_tokens=4000,
                context_length=200000,
                description="Fastest and most compact model",
                capabilities=["quick responses", "simple tasks", "summarization"]
            )
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate Anthropic model"""
        valid_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
        return model in valid_models


class GoogleProvider(BaseProvider):
    """Google Gemini API provider"""
    
    def _setup_client(self):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Generative AI library not available")
        
        genai.configure(api_key=self.config.api_key)
        self.client = genai
    
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using Google Gemini API"""
        try:
            model_instance = self.client.GenerativeModel(model)
            
            response = await model_instance.agenerate_content(
                prompt,
                generation_config=self.client.types.GenerationConfig(
                    max_output_tokens=parameters.get("max_tokens", 1000),
                    temperature=parameters.get("temperature", 0.7),
                    top_p=parameters.get("top_p", 1.0),
                    top_k=parameters.get("top_k", 40)
                )
            )
            
            response_text = response.text.strip()
            metadata = {
                "model": model,
                "provider": "google",
                "usage": {
                    "prompt_token_count": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                    "candidates_token_count": response.usage_metadata.candidates_token_count if response.usage_metadata else 0
                },
                "finish_reason": response.candidates[0].finish_reason if response.candidates else None,
                "parameters": parameters
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available Google models"""
        return [
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                provider="google",
                max_tokens=4000,
                context_length=1000000,
                description="Most capable Gemini model with long context",
                capabilities=["complex reasoning", "long documents", "multimodal"]
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                provider="google",
                max_tokens=4000,
                context_length=1000000,
                description="Fast and efficient Gemini model",
                capabilities=["quick responses", "general tasks", "summarization"]
            ),
            ModelInfo(
                id="gemini-pro",
                name="Gemini Pro",
                provider="google",
                max_tokens=4000,
                context_length=32768,
                description="Standard Gemini model",
                capabilities=["general tasks", "analysis", "writing"]
            )
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate Google model"""
        valid_models = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        return model in valid_models


class GroqProvider(BaseProvider):
    """Groq API provider"""
    
    def _setup_client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available (required for Groq)")
        
        # Groq uses OpenAI-compatible API
        openai.api_key = self.config.api_key
        openai.api_base = "https://api.groq.com/openai/v1"
        self.client = openai
    
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using Groq API"""
        try:
            response = await self.client.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=parameters.get("max_tokens", 1000),
                temperature=parameters.get("temperature", 0.7),
                top_p=parameters.get("top_p", 1.0),
                timeout=self.config.timeout
            )
            
            response_text = response.choices[0].message.content.strip()
            metadata = {
                "model": model,
                "provider": "groq",
                "usage": response.usage.dict() if response.usage else {},
                "finish_reason": response.choices[0].finish_reason,
                "parameters": parameters
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available Groq models"""
        return [
            ModelInfo(
                id="llama3-70b-8192",
                name="Llama 3 70B",
                provider="groq",
                max_tokens=4000,
                context_length=8192,
                description="Fast Llama 3 70B model",
                capabilities=["general tasks", "fast inference"]
            ),
            ModelInfo(
                id="llama3-8b-8192",
                name="Llama 3 8B",
                provider="groq",
                max_tokens=4000,
                context_length=8192,
                description="Fast Llama 3 8B model",
                capabilities=["quick responses", "simple tasks"]
            ),
            ModelInfo(
                id="mixtral-8x7b-32768",
                name="Mixtral 8x7B",
                provider="groq",
                max_tokens=4000,
                context_length=32768,
                description="Fast Mixtral model",
                capabilities=["general tasks", "long context"]
            )
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate Groq model"""
        valid_models = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
        return model in valid_models


class CustomProvider(BaseProvider):
    """Custom provider for any OpenAI-compatible API"""
    
    def _setup_client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        openai.api_key = self.config.api_key
        openai.api_base = self.config.base_url
        self.client = openai
    
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using custom API"""
        try:
            response = await self.client.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=parameters.get("max_tokens", 1000),
                temperature=parameters.get("temperature", 0.7),
                top_p=parameters.get("top_p", 1.0),
                timeout=self.config.timeout
            )
            
            response_text = response.choices[0].message.content.strip()
            metadata = {
                "model": model,
                "provider": "custom",
                "usage": response.usage.dict() if response.usage else {},
                "finish_reason": response.choices[0].finish_reason,
                "parameters": parameters
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Custom API error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get available custom models"""
        # This would typically be fetched from the API
        return [
            ModelInfo(
                id="custom-model",
                name="Custom Model",
                provider="custom",
                max_tokens=4000,
                description="Custom model from your API",
                capabilities=["general tasks"]
            )
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate custom model - assumes all models are valid"""
        return True


class ProviderManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self.model_mapping: Dict[str, str] = {}  # model_id -> provider_name
    
    def add_provider(self, name: str, provider: BaseProvider):
        """Add a provider to the manager"""
        self.providers[name] = provider
        
        # Update model mapping
        for model_info in provider.get_available_models():
            self.model_mapping[model_info.id] = name
    
    def get_provider_for_model(self, model: str) -> Optional[BaseProvider]:
        """Get the provider for a specific model"""
        provider_name = self.model_mapping.get(model)
        if provider_name:
            return self.providers.get(provider_name)
        return None
    
    def get_all_models(self) -> List[ModelInfo]:
        """Get all available models from all providers"""
        all_models = []
        for provider in self.providers.values():
            all_models.extend(provider.get_available_models())
        return all_models
    
    def validate_model(self, model: str) -> bool:
        """Validate if a model is supported by any provider"""
        return model in self.model_mapping
    
    async def generate(
        self, 
        prompt: str, 
        model: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using the appropriate provider"""
        provider = self.get_provider_for_model(model)
        if not provider:
            raise ValueError(f"No provider found for model: {model}")
        
        return await provider.generate(prompt, model, parameters)


# Global provider manager instance
provider_manager = ProviderManager() 