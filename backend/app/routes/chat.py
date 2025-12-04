# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Chat routes for interacting with AI agents
"""
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app.models import Agent, Purchase
from app.llm_service import LLMService

bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/agent/<int:agent_id>')
@login_required
def agent_chat(agent_id):
    """Chat interface for a specific agent."""
    agent = Agent.query.get_or_404(agent_id)

    # Check if user has purchased this agent
    has_purchased = Purchase.query.filter_by(
        buyer_id=current_user.id,
        agent_id=agent_id,
        is_active=True
    ).first()

    if not has_purchased:
        return jsonify({'error': 'You must purchase this agent before chatting'}), 403

    # Initialize conversation history in session
    session_key = f'chat_history_{agent_id}'
    if session_key not in session:
        session[session_key] = []

    if request.is_json:
        return jsonify({
            'agent': {
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'category': agent.category
            },
            'conversation_history': session.get(session_key, [])
        }), 200

    return render_template('chat/agent_chat.html', agent=agent)


@bp.route('/agent/<int:agent_id>/message', methods=['POST'])
@login_required
def send_message(agent_id):
    """Send a message to an agent and get response."""
    agent = Agent.query.get_or_404(agent_id)

    # Check if user has purchased this agent
    has_purchased = Purchase.query.filter_by(
        buyer_id=current_user.id,
        agent_id=agent_id,
        is_active=True
    ).first()

    if not has_purchased:
        return jsonify({'error': 'You must purchase this agent before chatting'}), 403

    # Get message and API key from request
    data = request.get_json()
    user_message = data.get('message')
    anthropic_api_key = data.get('api_key')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Determine which API key to use
    api_key = None
    if anthropic_api_key:
        # User provided API key with this request
        api_key = anthropic_api_key
        # Only save to session if not already saved (first message)
        if 'anthropic_api_key' not in session:
            session['anthropic_api_key'] = anthropic_api_key
    else:
        # Try to get from session
        api_key = session.get('anthropic_api_key')

    if not api_key:
        return jsonify({'error': 'Please provide your Anthropic API key', 'require_api_key': True}), 401

    # Get conversation history from session
    session_key = f'chat_history_{agent_id}'
    conversation_history = session.get(session_key, [])

    try:
        # Determine LLM provider (use agent's preference or detect from API key)
        llm_provider = agent.llm_provider if hasattr(agent, 'llm_provider') and agent.llm_provider else 'anthropic'

        # Initialize LLM service with provider
        llm_service = LLMService(provider=llm_provider, api_key=api_key)
        result = llm_service.chat(
            system_prompt=agent.system_prompt,
            conversation_history=conversation_history,
            user_message=user_message
        )

        # Update conversation history
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        conversation_history.append({
            'role': 'assistant',
            'content': result['response']
        })

        # Store updated history (limit to last 20 messages to avoid session size issues)
        session[session_key] = conversation_history[-20:]

        return jsonify({
            'response': result['response'],
            'model': result['model'],
            'usage': result['usage'],
            'provider': result['provider']
        }), 200

    except Exception as e:
        # Check if it's an authentication error
        error_str = str(e)
        if 'authentication' in error_str.lower() or ('invalid' in error_str.lower() and 'key' in error_str.lower()):
            # Clear invalid API key from session
            session.pop('anthropic_api_key', None)
            return jsonify({'error': f'Invalid API key. Please check your {LLMService.get_provider_name(llm_provider)} API key and try again.', 'require_api_key': True}), 401
        return jsonify({'error': str(e)}), 500


@bp.route('/agent/<int:agent_id>/clear', methods=['POST'])
@login_required
def clear_history(agent_id):
    """Clear conversation history for an agent."""
    agent = Agent.query.get_or_404(agent_id)

    # Check if user has purchased this agent
    has_purchased = Purchase.query.filter_by(
        buyer_id=current_user.id,
        agent_id=agent_id,
        is_active=True
    ).first()

    if not has_purchased:
        return jsonify({'error': 'You must purchase this agent before clearing history'}), 403

    # Clear session
    session_key = f'chat_history_{agent_id}'
    session.pop(session_key, None)

    return jsonify({'message': 'Conversation history cleared'}), 200
