"""
Anthropic Claude API service for AI agent interactions
"""
import anthropic
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Anthropic Claude API."""

    def __init__(self):
        """Initialize Claude client with API key from config."""
        self.api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not configured")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def chat_with_agent(self, system_prompt, conversation_history, user_message):
        """
        Send a message to Claude with the agent's system prompt.

        Args:
            system_prompt: The agent's specialized system prompt
            conversation_history: List of previous messages [{'role': 'user'/'assistant', 'content': '...'}]
            user_message: The new message from the user

        Returns:
            dict: {'response': str, 'model': str, 'usage': dict}
        """
        if not self.client:
            raise Exception("Claude API key not configured. Please set ANTHROPIC_API_KEY in your environment.")

        try:
            # Build messages list
            messages = conversation_history.copy()
            messages.append({
                'role': 'user',
                'content': user_message
            })

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using latest Sonnet model
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )

            # Extract response
            assistant_message = response.content[0].text

            return {
                'response': assistant_message,
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Failed to communicate with AI agent: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Claude service: {str(e)}")
            raise Exception(f"An error occurred: {str(e)}")

    def validate_agent_system_prompt(self, system_prompt):
        """
        Validate that an agent's system prompt is ethical and appropriate.
        Uses Claude to review the prompt for harmful content.

        Args:
            system_prompt: The proposed system prompt for a new agent

        Returns:
            dict: {'is_ethical': bool, 'concerns': list, 'suggestions': str}
        """
        if not self.client:
            raise Exception("Claude API key not configured")

        try:
            review_prompt = f"""You are an AI ethics reviewer for a marketplace of specialized AI agents.
Your job is to review system prompts to ensure they align with ethical AI principles and promote positive outcomes for humanity.

Review the following system prompt and determine:
1. Is it ethical and safe?
2. Does it promote positive outcomes for users and society?
3. Could it be misused for harmful purposes?
4. Does it respect privacy, fairness, and human autonomy?

System prompt to review:
---
{system_prompt}
---

Respond with a JSON object:
{{
  "is_ethical": true/false,
  "concerns": ["list", "of", "specific", "concerns"],
  "suggestions": "suggestions for improvement if needed"
}}"""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{
                    'role': 'user',
                    'content': review_prompt
                }]
            )

            # Parse response (basic implementation - could be enhanced)
            import json
            result = response.content[0].text

            # Try to extract JSON
            try:
                # Look for JSON in the response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    return json.loads(json_str)
            except:
                pass

            # Fallback if JSON parsing fails
            return {
                'is_ethical': True,
                'concerns': [],
                'suggestions': 'Manual review recommended'
            }

        except Exception as e:
            logger.error(f"Error validating system prompt: {str(e)}")
            # Default to requiring manual review
            return {
                'is_ethical': False,
                'concerns': ['Automatic validation failed'],
                'suggestions': 'Manual review required'
            }
