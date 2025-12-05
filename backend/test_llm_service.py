#!/usr/bin/env python3
"""Test LLM Service with multiple providers"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.llm_service import LLMService

def test_provider_detection():
    """Test API key provider detection"""
    print("Testing provider detection...")

    # Test Anthropic key detection
    anthropic_key = "sk-ant-api03-test"
    provider = LLMService.get_provider_for_key(anthropic_key)
    assert provider == 'anthropic', f"Expected 'anthropic', got '{provider}'"
    print("✓ Anthropic key detection works")

    # Test OpenAI key detection
    openai_key = "sk-test123"
    provider = LLMService.get_provider_for_key(openai_key)
    assert provider == 'openai', f"Expected 'openai', got '{provider}'"
    print("✓ OpenAI key detection works")

def test_provider_initialization():
    """Test provider initialization"""
    print("\nTesting provider initialization...")

    # Test Anthropic initialization
    try:
        service = LLMService(provider='anthropic', api_key='sk-ant-api03-test')
        print(f"✓ Anthropic provider initialized: {service.provider_info['name']}")
    except Exception as e:
        print(f"✗ Anthropic initialization failed: {e}")
        return False

    # Test OpenAI initialization
    try:
        service = LLMService(provider='openai', api_key='sk-test123')
        print(f"✓ OpenAI provider initialized: {service.provider_info['name']}")
    except Exception as e:
        print(f"✗ OpenAI initialization failed: {e}")
        return False

    return True

def test_supported_providers():
    """Test supported providers list"""
    print("\nTesting supported providers...")

    providers = LLMService.SUPPORTED_PROVIDERS
    print(f"Supported providers: {list(providers.keys())}")

    assert 'anthropic' in providers, "Anthropic not in supported providers"
    assert 'openai' in providers, "OpenAI not in supported providers"

    print(f"✓ Anthropic: {providers['anthropic']['name']}")
    print(f"  Models: {', '.join(providers['anthropic']['models'])}")
    print(f"✓ OpenAI: {providers['openai']['name']}")
    print(f"  Models: {', '.join(providers['openai']['models'])}")

def test_api_key_validation():
    """Test API key validation"""
    print("\nTesting API key validation...")

    # Anthropic key validation
    valid = LLMService.validate_api_key('anthropic', 'sk-ant-api03-test')
    assert valid, "Valid Anthropic key rejected"
    print("✓ Anthropic key validation works")

    invalid = LLMService.validate_api_key('anthropic', 'invalid-key')
    assert not invalid, "Invalid Anthropic key accepted"
    print("✓ Anthropic key rejection works")

    # OpenAI key validation
    valid = LLMService.validate_api_key('openai', 'sk-test123')
    assert valid, "Valid OpenAI key rejected"
    print("✓ OpenAI key validation works")

    invalid = LLMService.validate_api_key('openai', 'sk-ant-api03-test')
    assert not invalid, "Invalid OpenAI key (Anthropic key) accepted"
    print("✓ OpenAI key rejection works")

def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM Service Test Suite")
    print("=" * 60)

    try:
        test_supported_providers()
        test_provider_detection()
        test_api_key_validation()
        test_provider_initialization()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
