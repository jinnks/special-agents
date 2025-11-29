# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Chat routes for interacting with AI agents
"""
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app.models import Agent, Purchase
from app.claude_service import ClaudeService

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

    # Get message from request
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Get conversation history from session
    session_key = f'chat_history_{agent_id}'
    conversation_history = session.get(session_key, [])

    try:
        # Call Claude API
        claude_service = ClaudeService()
        result = claude_service.chat_with_agent(
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
            'usage': result['usage']
        }), 200

    except Exception as e:
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
