# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Simplified agent creation routes
Hybrid approach: web form, templates, and advanced .sagent upload
"""
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Agent, AgentConfig, AgentPricing, AgentStats
from app.security import InputValidator
from app.agent_templates import get_all_templates, get_template

bp = Blueprint('agent_creator', __name__, url_prefix='/agent/create')


@bp.route('/choose-mode', methods=['GET'])
@login_required
def choose_mode():
    """Step 1: Choose how to create the agent"""
    if not current_user.is_seller:
        flash('You must be a seller to create agents', 'error')
        return redirect(url_for('main.index'))

    return render_template('agent_creator/choose_mode.html')


@bp.route('/from-scratch', methods=['GET', 'POST'])
@login_required
def from_scratch():
    """Beginner Mode: Create agent from scratch with guided web form"""
    if not current_user.is_seller:
        flash('You must be a seller to create agents', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.form

        # Validate inputs
        name = InputValidator.sanitize_text(data.get('name', ''), max_length=200)
        valid, error = InputValidator.validate_agent_name(name)
        if not valid:
            flash(error, 'error')
            return redirect(url_for('agent_creator.from_scratch'))

        description = InputValidator.sanitize_text(data.get('description', ''), max_length=2000)
        if not description or len(description) < 20:
            flash('Description must be at least 20 characters', 'error')
            return redirect(url_for('agent_creator.from_scratch'))

        category = data.get('category', '')
        valid, error = InputValidator.validate_category(category)
        if not valid:
            flash(error, 'error')
            return redirect(url_for('agent_creator.from_scratch'))

        # System prompt (user-friendly wording: "How should your agent behave?")
        system_prompt = InputValidator.sanitize_text(data.get('system_prompt', ''), max_length=5000)
        if not system_prompt or len(system_prompt) < 50:
            flash('Agent behavior instructions must be at least 50 characters', 'error')
            return redirect(url_for('agent_creator.from_scratch'))

        llm_provider = data.get('llm_provider', 'anthropic')
        if llm_provider not in ['anthropic', 'openai']:
            flash('Invalid LLM provider', 'error')
            return redirect(url_for('agent_creator.from_scratch'))

        price = data.get('price', '9.99')
        valid, error = InputValidator.validate_price(price)
        if not valid:
            flash(error, 'error')
            return redirect(url_for('agent_creator.from_scratch'))

        # Parse example conversations if provided
        example_conversations = []
        for i in range(1, 4):  # Up to 3 examples
            user_msg = data.get(f'example_user_{i}', '').strip()
            agent_msg = data.get(f'example_agent_{i}', '').strip()
            if user_msg and agent_msg:
                example_conversations.append({
                    'user': InputValidator.sanitize_text(user_msg, max_length=500),
                    'assistant': InputValidator.sanitize_text(agent_msg, max_length=1000)
                })

        try:
            # Create agent
            agent = Agent(
                name=name,
                description=description,
                category=category,
                creator_id=current_user.id,
                is_active=True,
                is_approved=False  # Requires moderation
            )
            db.session.add(agent)
            db.session.flush()

            # Create config
            config = AgentConfig(
                agent_id=agent.id,
                system_prompt=system_prompt,
                llm_provider=llm_provider,
                creation_mode='web_form',
                example_conversations=json.dumps(example_conversations) if example_conversations else None
            )
            db.session.add(config)

            # Create pricing
            pricing = AgentPricing(
                agent_id=agent.id,
                price=float(price),
                currency='USD'
            )
            db.session.add(pricing)

            # Create stats
            stats = AgentStats(
                agent_id=agent.id,
                purchase_count=0,
                average_rating=0.0
            )
            db.session.add(stats)

            db.session.commit()

            flash('Agent created successfully! It will be available after approval.', 'success')
            return redirect(url_for('agents.agent_detail', agent_id=agent.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating agent: {str(e)}', 'error')
            return redirect(url_for('agent_creator.from_scratch'))

    return render_template('agent_creator/from_scratch.html')


@bp.route('/from-template', methods=['GET'])
@login_required
def from_template():
    """Template Mode: Browse and select templates"""
    if not current_user.is_seller:
        flash('You must be a seller to create agents', 'error')
        return redirect(url_for('main.index'))

    templates = get_all_templates()
    return render_template('agent_creator/from_template.html', templates=templates)


@bp.route('/from-template/<template_id>', methods=['GET', 'POST'])
@login_required
def customize_template(template_id):
    """Customize a selected template"""
    if not current_user.is_seller:
        flash('You must be a seller to create agents', 'error')
        return redirect(url_for('main.index'))

    template = get_template(template_id)
    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('agent_creator.from_template'))

    if request.method == 'POST':
        data = request.form

        # Get customized values (fallback to template defaults)
        name = InputValidator.sanitize_text(data.get('name', template['name']), max_length=200)
        description = InputValidator.sanitize_text(data.get('description', template['description']), max_length=2000)
        system_prompt = InputValidator.sanitize_text(data.get('system_prompt', template['system_prompt']), max_length=5000)
        category = data.get('category', template['category'])
        llm_provider = data.get('llm_provider', 'anthropic')
        price = data.get('price', '9.99')

        # Validation
        valid, error = InputValidator.validate_agent_name(name)
        if not valid:
            flash(error, 'error')
            return redirect(url_for('agent_creator.customize_template', template_id=template_id))

        valid, error = InputValidator.validate_price(price)
        if not valid:
            flash(error, 'error')
            return redirect(url_for('agent_creator.customize_template', template_id=template_id))

        try:
            # Create agent
            agent = Agent(
                name=name,
                description=description,
                category=category,
                creator_id=current_user.id,
                is_active=True,
                is_approved=False
            )
            db.session.add(agent)
            db.session.flush()

            # Create config
            config = AgentConfig(
                agent_id=agent.id,
                system_prompt=system_prompt,
                llm_provider=llm_provider,
                creation_mode='template',
                template_id=template_id,
                example_conversations=json.dumps(template.get('example_conversations', []))
            )
            db.session.add(config)

            # Create pricing
            pricing = AgentPricing(
                agent_id=agent.id,
                price=float(price),
                currency='USD'
            )
            db.session.add(pricing)

            # Create stats
            stats = AgentStats(
                agent_id=agent.id,
                purchase_count=0,
                average_rating=0.0
            )
            db.session.add(stats)

            db.session.commit()

            flash(f'Agent created from template "{template["name"]}"! It will be available after approval.', 'success')
            return redirect(url_for('agents.agent_detail', agent_id=agent.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating agent: {str(e)}', 'error')
            return redirect(url_for('agent_creator.customize_template', template_id=template_id))

    return render_template('agent_creator/customize_template.html', template=template, template_id=template_id)


@bp.route('/preview', methods=['POST'])
@login_required
def preview_agent():
    """API endpoint for live preview/testing agent before creation"""
    data = request.get_json()

    system_prompt = data.get('system_prompt', '')
    user_message = data.get('message', '')
    conversation_history = data.get('conversation_history', [])
    llm_provider = data.get('llm_provider', 'anthropic')

    if not system_prompt or not user_message:
        return jsonify({'error': 'Missing system prompt or message'}), 400

    try:
        # Check if user has provided their own API key
        from flask import session
        from app.llm_service import LLMService
        from app.security import APIKeyEncryption

        user_api_key = None
        if 'user_api_key' in session:
            encrypted_key = session.get('user_api_key')
            user_api_key = APIKeyEncryption.decrypt(encrypted_key)
            provider_from_session = session.get('user_llm_provider', llm_provider)
            llm_provider = provider_from_session

        if not user_api_key:
            return jsonify({
                'error': 'Please provide your API key to test the agent',
                'redirect': url_for('chat.chat_with_key')
            }), 403

        # Use LLM service to get response
        llm_service = LLMService(llm_provider, user_api_key)
        result = llm_service.chat(system_prompt, conversation_history, user_message)

        return jsonify({
            'response': result['response'],
            'model': result['model'],
            'usage': result['usage']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
