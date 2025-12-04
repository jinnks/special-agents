# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Unified LLM service supporting multiple providers (Anthropic, OpenAI, etc.)
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(self, system_prompt: str, messages: List[Dict], max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Send a chat request to the LLM.

        Args:
            system_prompt: System instructions for the AI
            messages: List of conversation messages [{'role': 'user'/'assistant', 'content': '...'}]
            max_tokens: Maximum tokens to generate

        Returns:
            dict: {'response': str, 'model': str, 'usage': dict}
        """
        pass

    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.api_key = api_key

    def chat(self, system_prompt: str, messages: List[Dict], max_tokens: int = 4096) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            )

            return {
                'response': response.content[0].text,
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise Exception(f"Failed to communicate with Claude: {str(e)}")

    def validate_api_key(self, api_key: str) -> bool:
        return api_key.startswith('sk-ant-')


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key

    def chat(self, system_prompt: str, messages: List[Dict], max_tokens: int = 4096) -> Dict[str, Any]:
        try:
            # Convert messages format - OpenAI expects system message in messages array
            openai_messages = [{'role': 'system', 'content': system_prompt}]
            openai_messages.extend(messages)

            response = self.client.chat.completions.create(
                model="gpt-4o",  # Latest GPT-4 model
                max_tokens=max_tokens,
                messages=openai_messages
            )

            return {
                'response': response.choices[0].message.content,
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to communicate with GPT: {str(e)}")

    def validate_api_key(self, api_key: str) -> bool:
        return api_key.startswith('sk-') and not api_key.startswith('sk-ant-')


class LLMService:
    """Unified LLM service supporting multiple providers."""

    SUPPORTED_PROVIDERS = {
        'anthropic': {
            'name': 'Anthropic Claude',
            'models': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
            'key_prefix': 'sk-ant-',
            'provider_class': AnthropicProvider
        },
        'openai': {
            'name': 'OpenAI GPT',
            'models': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'key_prefix': 'sk-',
            'provider_class': OpenAIProvider
        }
    }

    def __init__(self, provider: str, api_key: str):
        """
        Initialize LLM service with specified provider.

        Args:
            provider: Provider ID ('anthropic', 'openai', etc.)
            api_key: API key for the provider

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        self.provider_id = provider
        self.provider_info = self.SUPPORTED_PROVIDERS[provider]

        # Initialize provider
        provider_class = self.provider_info['provider_class']
        self.provider = provider_class(api_key)

    def chat(self, system_prompt: str, conversation_history: List[Dict], user_message: str) -> Dict[str, Any]:
        """
        Send a message to the LLM.

        Args:
            system_prompt: The agent's system prompt
            conversation_history: Previous messages
            user_message: New message from user

        Returns:
            dict: {'response': str, 'model': str, 'usage': dict, 'provider': str}
        """
        # Build messages
        messages = conversation_history.copy()
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # Call provider
        result = self.provider.chat(system_prompt, messages)
        result['provider'] = self.provider_id

        return result

    @classmethod
    def get_provider_name(cls, provider_id: str) -> str:
        """Get human-readable provider name."""
        return cls.SUPPORTED_PROVIDERS.get(provider_id, {}).get('name', provider_id)

    @classmethod
    def get_provider_for_key(cls, api_key: str) -> str:
        """Detect provider from API key format."""
        if api_key.startswith('sk-ant-'):
            return 'anthropic'
        elif api_key.startswith('sk-'):
            return 'openai'
        else:
            raise ValueError("Unable to detect LLM provider from API key format")

    @classmethod
    def validate_api_key(cls, provider: str, api_key: str) -> bool:
        """Validate API key format for provider."""
        if provider not in cls.SUPPORTED_PROVIDERS:
            return False

        provider_class = cls.SUPPORTED_PROVIDERS[provider]['provider_class']
        temp_provider = provider_class.__new__(provider_class)
        return temp_provider.validate_api_key(api_key)
