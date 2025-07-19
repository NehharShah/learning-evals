#!/usr/bin/env python3
"""
Test script for multi-provider LLM integration
Tests the provider system with different API configurations
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.providers import (
    provider_manager,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    GroqProvider,
    CustomProvider,
    ProviderConfig,
    ModelInfo
)


async def test_provider_initialization():
    """Test provider initialization with different configurations"""
    print("🧪 Testing Provider Initialization")
    print("=" * 50)
    
    # Test OpenAI provider
    if os.getenv("OPENAI_API_KEY"):
        try:
            openai_config = ProviderConfig(
                name="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                timeout=30
            )
            openai_provider = OpenAIProvider(openai_config)
            provider_manager.add_provider("openai", openai_provider)
            print("✅ OpenAI provider initialized successfully")
            
            # Test model validation
            assert openai_provider.validate_model("gpt-3.5-turbo") == True
            assert openai_provider.validate_model("invalid-model") == False
            print("✅ OpenAI model validation working")
            
        except Exception as e:
            print(f"❌ OpenAI provider initialization failed: {e}")
    else:
        print("⚠️  OpenAI API key not found, skipping OpenAI tests")
    
    # Test Anthropic provider
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            anthropic_config = ProviderConfig(
                name="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=30
            )
            anthropic_provider = AnthropicProvider(anthropic_config)
            provider_manager.add_provider("anthropic", anthropic_provider)
            print("✅ Anthropic provider initialized successfully")
            
            # Test model validation
            assert anthropic_provider.validate_model("claude-3-sonnet-20240229") == True
            assert anthropic_provider.validate_model("invalid-model") == False
            print("✅ Anthropic model validation working")
            
        except Exception as e:
            print(f"❌ Anthropic provider initialization failed: {e}")
    else:
        print("⚠️  Anthropic API key not found, skipping Anthropic tests")
    
    # Test Google provider
    if os.getenv("GOOGLE_API_KEY"):
        try:
            google_config = ProviderConfig(
                name="google",
                api_key=os.getenv("GOOGLE_API_KEY"),
                timeout=30
            )
            google_provider = GoogleProvider(google_config)
            provider_manager.add_provider("google", google_provider)
            print("✅ Google provider initialized successfully")
            
            # Test model validation
            assert google_provider.validate_model("gemini-pro") == True
            assert google_provider.validate_model("invalid-model") == False
            print("✅ Google model validation working")
            
        except Exception as e:
            print(f"❌ Google provider initialization failed: {e}")
    else:
        print("⚠️  Google API key not found, skipping Google tests")
    
    # Test Groq provider
    if os.getenv("GROQ_API_KEY"):
        try:
            groq_config = ProviderConfig(
                name="groq",
                api_key=os.getenv("GROQ_API_KEY"),
                timeout=30
            )
            groq_provider = GroqProvider(groq_config)
            provider_manager.add_provider("groq", groq_provider)
            print("✅ Groq provider initialized successfully")
            
            # Test model validation
            assert groq_provider.validate_model("llama3-70b-8192") == True
            assert groq_provider.validate_model("invalid-model") == False
            print("✅ Groq model validation working")
            
        except Exception as e:
            print(f"❌ Groq provider initialization failed: {e}")
    else:
        print("⚠️  Groq API key not found, skipping Groq tests")
    
    print(f"\n📊 Provider Summary: {len(provider_manager.providers)} providers initialized")


async def test_model_discovery():
    """Test model discovery across all providers"""
    print("\n🧪 Testing Model Discovery")
    print("=" * 50)
    
    all_models = provider_manager.get_all_models()
    print(f"📋 Total models discovered: {len(all_models)}")
    
    # Group models by provider
    models_by_provider = {}
    for model in all_models:
        if model.provider not in models_by_provider:
            models_by_provider[model.provider] = []
        models_by_provider[model.provider].append(model)
    
    for provider, models in models_by_provider.items():
        print(f"\n🔹 {provider.upper()} ({len(models)} models):")
        for model in models:
            print(f"   • {model.name} ({model.id})")
            print(f"     Max tokens: {model.max_tokens:,}")
            if model.context_length:
                print(f"     Context: {model.context_length:,}")
            if model.description:
                print(f"     Description: {model.description}")
            if model.capabilities:
                print(f"     Capabilities: {', '.join(model.capabilities)}")
            print()


async def test_provider_mapping():
    """Test provider mapping functionality"""
    print("\n🧪 Testing Provider Mapping")
    print("=" * 50)
    
    # Test model to provider mapping
    test_cases = [
        ("gpt-3.5-turbo", "openai"),
        ("claude-3-sonnet-20240229", "anthropic"),
        ("gemini-pro", "google"),
        ("llama3-70b-8192", "groq"),
    ]
    
    for model_id, expected_provider in test_cases:
        provider = provider_manager.get_provider_for_model(model_id)
        if provider:
            print(f"✅ {model_id} -> {provider.config.name}")
            assert provider.config.name == expected_provider
        else:
            print(f"⚠️  No provider found for {model_id}")
    
    # Test invalid model
    invalid_provider = provider_manager.get_provider_for_model("invalid-model")
    assert invalid_provider is None
    print("✅ Invalid model correctly returns no provider")


async def test_api_generation():
    """Test actual API generation (if API keys are available)"""
    print("\n🧪 Testing API Generation")
    print("=" * 50)
    
    test_prompt = "What is the capital of France?"
    test_parameters = {
        "max_tokens": 50,
        "temperature": 0.7,
        "top_p": 1.0
    }
    
    # Test with first available model
    all_models = provider_manager.get_all_models()
    if not all_models:
        print("⚠️  No models available for testing")
        return
    
    test_model = all_models[0]
    print(f"🔹 Testing with model: {test_model.name} ({test_model.provider})")
    
    try:
        provider = provider_manager.get_provider_for_model(test_model.id)
        if provider:
            response_text, metadata = await provider.generate(
                test_prompt, 
                test_model.id, 
                test_parameters
            )
            
            print(f"✅ Generation successful!")
            print(f"   Response: {response_text[:100]}...")
            print(f"   Provider: {metadata.get('provider', 'unknown')}")
            print(f"   Model: {metadata.get('model', 'unknown')}")
            print(f"   Usage: {metadata.get('usage', {})}")
            
        else:
            print(f"❌ No provider found for model {test_model.id}")
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print("   This might be due to missing API key or network issues")


async def test_provider_manager():
    """Test provider manager functionality"""
    print("\n🧪 Testing Provider Manager")
    print("=" * 50)
    
    # Test model validation
    all_models = provider_manager.get_all_models()
    for model in all_models[:3]:  # Test first 3 models
        is_valid = provider_manager.validate_model(model.id)
        print(f"✅ {model.id}: {'Valid' if is_valid else 'Invalid'}")
    
    # Test invalid model
    is_invalid = provider_manager.validate_model("invalid-model-123")
    print(f"✅ Invalid model validation: {'Correctly invalid' if not is_invalid else 'Incorrectly valid'}")
    
    # Test provider count
    print(f"📊 Total providers: {len(provider_manager.providers)}")
    print(f"📊 Total models: {len(provider_manager.model_mapping)}")


async def main():
    """Main test function"""
    print("🚀 Multi-Provider LLM Integration Test")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        await test_provider_initialization()
        await test_model_discovery()
        await test_provider_mapping()
        await test_provider_manager()
        await test_api_generation()
        
        print("\n🎉 All tests completed!")
        print("\n📝 Summary:")
        print(f"   • Providers initialized: {len(provider_manager.providers)}")
        print(f"   • Models available: {len(provider_manager.get_all_models())}")
        print(f"   • Model mappings: {len(provider_manager.model_mapping)}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 