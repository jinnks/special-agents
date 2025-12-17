# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Unit tests for LLM service
Fast, isolated tests with mocked API calls
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.llm_service import LLMService, AnthropicProvider, OpenAIProvider


class TestLLMService:
    """Test LLM Service main class"""

    @patch('anthropic.Anthropic')
    def test_init_anthropic_provider(self, mock_anthropic):
        service = LLMService('anthropic', 'sk-ant-test')
        assert service.provider_id == 'anthropic'
        assert isinstance(service.provider, AnthropicProvider)

    @patch('openai.OpenAI')
    def test_init_openai_provider(self, mock_openai):
        service = LLMService('openai', 'sk-test')
        assert service.provider_id == 'openai'
        assert isinstance(service.provider, OpenAIProvider)

    def test_init_invalid_provider(self):
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMService('invalid_provider', 'key')

    def test_get_provider_name_anthropic(self):
        name = LLMService.get_provider_name('anthropic')
        assert name == 'Anthropic Claude'

    def test_get_provider_name_openai(self):
        name = LLMService.get_provider_name('openai')
        assert name == 'OpenAI GPT'

    def test_get_provider_name_unknown(self):
        name = LLMService.get_provider_name('unknown')
        assert name == 'unknown'

    def test_get_provider_for_key_anthropic(self):
        provider = LLMService.get_provider_for_key('sk-ant-api03-test')
        assert provider == 'anthropic'

    def test_get_provider_for_key_openai(self):
        provider = LLMService.get_provider_for_key('sk-test123')
        assert provider == 'openai'

    def test_get_provider_for_key_invalid(self):
        with pytest.raises(ValueError, match="Unable to detect"):
            LLMService.get_provider_for_key('invalid-key')

    def test_validate_api_key_anthropic_valid(self):
        valid = LLMService.validate_api_key('anthropic', 'sk-ant-test')
        assert valid is True

    def test_validate_api_key_anthropic_invalid(self):
        valid = LLMService.validate_api_key('anthropic', 'invalid')
        assert valid is False

    def test_validate_api_key_openai_valid(self):
        valid = LLMService.validate_api_key('openai', 'sk-test')
        assert valid is True

    def test_validate_api_key_openai_invalid(self):
        valid = LLMService.validate_api_key('openai', 'sk-ant-test')
        assert valid is False

    def test_validate_api_key_invalid_provider(self):
        valid = LLMService.validate_api_key('invalid', 'key')
        assert valid is False

    @patch('anthropic.Anthropic')
    @patch('app.llm_service.AnthropicProvider.chat')
    def test_chat_success(self, mock_chat, mock_anthropic):
        mock_chat.return_value = {
            'response': 'Hello!',
            'model': 'claude-3-5-sonnet',
            'usage': {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}
        }

        service = LLMService('anthropic', 'sk-ant-test')
        result = service.chat('You are helpful', [], 'Hi')

        assert result['response'] == 'Hello!'
        assert result['provider'] == 'anthropic'
        assert 'usage' in result


class TestAnthropicProvider:
    """Test Anthropic provider"""

    def test_validate_api_key_valid(self):
        provider = Mock(spec=AnthropicProvider)
        provider.validate_api_key = AnthropicProvider.validate_api_key.__get__(provider)

        assert provider.validate_api_key('sk-ant-api03-test') is True

    def test_validate_api_key_invalid(self):
        provider = Mock(spec=AnthropicProvider)
        provider.validate_api_key = AnthropicProvider.validate_api_key.__get__(provider)

        assert provider.validate_api_key('invalid-key') is False

    @patch('anthropic.Anthropic')
    def test_chat_success(self, mock_anthropic_client):
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Hello from Claude!')]
        mock_response.model = 'claude-3-5-sonnet-20241022'
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=5)

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_client.return_value = mock_client

        provider = AnthropicProvider('sk-ant-test')
        result = provider.chat('You are helpful', [{'role': 'user', 'content': 'Hi'}])

        assert result['response'] == 'Hello from Claude!'
        assert result['model'] == 'claude-3-5-sonnet-20241022'
        assert result['usage']['input_tokens'] == 10
        assert result['usage']['output_tokens'] == 5

    @patch('anthropic.Anthropic')
    def test_chat_api_error(self, mock_anthropic_client):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception('API Error')
        mock_anthropic_client.return_value = mock_client

        provider = AnthropicProvider('sk-ant-test')

        with pytest.raises(Exception, match='Failed to communicate with Claude'):
            provider.chat('System', [])


class TestOpenAIProvider:
    """Test OpenAI provider"""

    def test_validate_api_key_valid(self):
        provider = Mock(spec=OpenAIProvider)
        provider.validate_api_key = OpenAIProvider.validate_api_key.__get__(provider)

        assert provider.validate_api_key('sk-test123') is True

    def test_validate_api_key_invalid(self):
        provider = Mock(spec=OpenAIProvider)
        provider.validate_api_key = OpenAIProvider.validate_api_key.__get__(provider)

        assert provider.validate_api_key('sk-ant-test') is False

    @patch('openai.OpenAI')
    def test_chat_success(self, mock_openai_client):
        # Mock response
        mock_message = MagicMock()
        mock_message.content = 'Hello from GPT!'

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 5
        mock_usage.total_tokens = 15

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = 'gpt-4o'
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client

        provider = OpenAIProvider('sk-test')
        result = provider.chat('You are helpful', [{'role': 'user', 'content': 'Hi'}])

        assert result['response'] == 'Hello from GPT!'
        assert result['model'] == 'gpt-4o'
        assert result['usage']['input_tokens'] == 10
        assert result['usage']['output_tokens'] == 5

    @patch('openai.OpenAI')
    def test_chat_api_error(self, mock_openai_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception('API Error')
        mock_openai_client.return_value = mock_client

        provider = OpenAIProvider('sk-test')

        with pytest.raises(Exception, match='Failed to communicate with GPT'):
            provider.chat('System', [])
