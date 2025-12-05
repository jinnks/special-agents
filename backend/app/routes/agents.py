# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Agent marketplace routes for browsing, creating, and managing agents
"""
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Agent, Purchase, Review, AgentConfig, AgentPricing, AgentStats, AgentPackage
from app.agent_package import AgentPackageValidator, AgentPackageExtractor
from sqlalchemy import func

bp = Blueprint('agents', __name__, url_prefix='/agents')


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def marketplace():
    """Browse all approved agents."""
    category = request.args.get('category')
    search = request.args.get('search')

    query = Agent.query.filter_by(is_approved=True, is_active=True)

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(
            (Agent.name.ilike(f'%{search}%')) |
            (Agent.description.ilike(f'%{search}%'))
        )

    # Order by stats (join with AgentStats table)
    agents = query.join(AgentStats, Agent.id == AgentStats.agent_id, isouter=True).order_by(
        AgentStats.average_rating.desc().nullslast(),
        AgentStats.purchase_count.desc().nullslast()
    ).all()

    if request.is_json:
        return jsonify({
            'agents': [{
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'category': agent.category,
                'price': agent.pricing.price if agent.pricing else 0.0,
                'currency': agent.pricing.currency if agent.pricing else 'USD',
                'average_rating': agent.stats.average_rating if agent.stats else 0.0,
                'purchase_count': agent.stats.purchase_count if agent.stats else 0,
                'creator': agent.creator.username
            } for agent in agents]
        }), 200

    return render_template('agents/marketplace.html', agents=agents)


@bp.route('/<int:agent_id>')
def detail(agent_id):
    """View agent details."""
    agent = Agent.query.get_or_404(agent_id)

    # Check if current user has purchased this agent
    has_purchased = False
    if current_user.is_authenticated:
        has_purchased = Purchase.query.filter_by(
            buyer_id=current_user.id,
            agent_id=agent_id,
            is_active=True
        ).first() is not None

    # Get reviews
    reviews = Review.query.filter_by(agent_id=agent_id, is_visible=True).order_by(
        Review.created_at.desc()
    ).all()

    if request.is_json:
        return jsonify({
            'agent': {
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'category': agent.category,
                'price': agent.pricing.price if agent.pricing else 0.0,
                'currency': agent.pricing.currency if agent.pricing else 'USD',
                'average_rating': agent.stats.average_rating if agent.stats else 0.0,
                'purchase_count': agent.stats.purchase_count if agent.stats else 0,
                'creator': agent.creator.username,
                'created_at': agent.created_at.isoformat()
            },
            'has_purchased': has_purchased,
            'reviews': [{
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'reviewer': review.reviewer.username,
                'created_at': review.created_at.isoformat()
            } for review in reviews]
        }), 200

    return render_template('agents/detail.html', agent=agent, has_purchased=has_purchased, reviews=reviews)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new agent (sellers only)."""
    if not current_user.is_seller:
        flash('You must be a seller to create agents', 'error')
        return redirect(url_for('agents.marketplace'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        name = data.get('name')
        description = data.get('description')
        system_prompt = data.get('system_prompt')
        category = data.get('category')
        price = float(data.get('price', 0))
        llm_provider = data.get('llm_provider', 'anthropic')

        if not name or not description or not system_prompt or not category:
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            flash('All fields are required', 'error')
            return redirect(url_for('agents.create'))

        # Validate llm_provider
        if llm_provider not in ['anthropic', 'openai']:
            llm_provider = 'anthropic'

        # Create agent (core info)
        agent = Agent(
            name=name,
            description=description,
            category=category,
            creator_id=current_user.id,
            is_approved=False  # Requires ethical review
        )
        db.session.add(agent)
        db.session.flush()  # Get agent.id for related records

        # Create agent config (AI settings)
        agent_config = AgentConfig(
            agent_id=agent.id,
            system_prompt=system_prompt,
            llm_provider=llm_provider
        )
        db.session.add(agent_config)

        # Create agent pricing
        agent_pricing = AgentPricing(
            agent_id=agent.id,
            price=price,
            currency='USD'
        )
        db.session.add(agent_pricing)

        # Create agent stats
        agent_stats = AgentStats(
            agent_id=agent.id,
            purchase_count=0,
            average_rating=0.0
        )
        db.session.add(agent_stats)

        db.session.commit()

        if request.is_json:
            return jsonify({
                'message': 'Agent created successfully (pending approval)',
                'agent_id': agent.id
            }), 201

        flash('Agent created! It will be reviewed for ethical compliance before being listed.', 'success')
        return redirect(url_for('agents.detail', agent_id=agent.id))

    return render_template('agents/create.html')


@bp.route('/<int:agent_id>/purchase', methods=['POST'])
@login_required
def purchase(agent_id):
    """Purchase an agent."""
    agent = Agent.query.get_or_404(agent_id)

    # Check if already purchased
    existing_purchase = Purchase.query.filter_by(
        buyer_id=current_user.id,
        agent_id=agent_id,
        is_active=True
    ).first()

    if existing_purchase:
        if request.is_json:
            return jsonify({'error': 'You already own this agent'}), 400
        flash('You already own this agent', 'error')
        return redirect(url_for('agents.detail', agent_id=agent_id))

    # Create purchase
    purchase = Purchase(
        buyer_id=current_user.id,
        agent_id=agent_id,
        price_paid=agent.pricing.price if agent.pricing else 0.0,
        currency=agent.pricing.currency if agent.pricing else 'USD'
    )
    db.session.add(purchase)

    # Update agent stats
    if agent.stats:
        agent.stats.purchase_count += 1
    db.session.commit()

    if request.is_json:
        return jsonify({'message': 'Purchase successful', 'purchase_id': purchase.id}), 201

    flash('Purchase successful! You can now chat with this agent.', 'success')
    return redirect(url_for('chat.agent_chat', agent_id=agent_id))


@bp.route('/<int:agent_id>/review', methods=['POST'])
@login_required
def add_review(agent_id):
    """Add a review for an agent."""
    agent = Agent.query.get_or_404(agent_id)

    # Check if user has purchased this agent
    has_purchased = Purchase.query.filter_by(
        buyer_id=current_user.id,
        agent_id=agent_id,
        is_active=True
    ).first()

    if not has_purchased:
        if request.is_json:
            return jsonify({'error': 'You must purchase this agent before reviewing'}), 403
        flash('You must purchase this agent before reviewing', 'error')
        return redirect(url_for('agents.detail', agent_id=agent_id))

    # Check if already reviewed
    existing_review = Review.query.filter_by(
        reviewer_id=current_user.id,
        agent_id=agent_id
    ).first()

    data = request.get_json() if request.is_json else request.form
    rating = int(data.get('rating'))
    comment = data.get('comment', '')

    if not 1 <= rating <= 5:
        if request.is_json:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        flash('Rating must be between 1 and 5', 'error')
        return redirect(url_for('agents.detail', agent_id=agent_id))

    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.comment = comment
    else:
        # Create new review
        review = Review(
            agent_id=agent_id,
            reviewer_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)

    db.session.commit()

    # Recalculate average rating
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
        agent_id=agent_id,
        is_visible=True
    ).scalar()
    if agent.stats:
        agent.stats.average_rating = round(avg_rating, 2) if avg_rating else 0.0
    db.session.commit()

    if request.is_json:
        return jsonify({'message': 'Review submitted successfully'}), 201

    flash('Review submitted successfully!', 'success')
    return redirect(url_for('agents.detail', agent_id=agent_id))


@bp.route('/my-agents')
@login_required
def my_agents():
    """View agents created by current user (sellers only)."""
    if not current_user.is_seller:
        flash('You must be a seller to view this page', 'error')
        return redirect(url_for('agents.marketplace'))

    agents = Agent.query.filter_by(creator_id=current_user.id).order_by(
        Agent.created_at.desc()
    ).all()

    if request.is_json:
        return jsonify({
            'agents': [{
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'category': agent.category,
                'price': agent.pricing.price if agent.pricing else 0.0,
                'is_approved': agent.is_approved,
                'is_active': agent.is_active,
                'purchase_count': agent.stats.purchase_count if agent.stats else 0,
                'average_rating': agent.stats.average_rating if agent.stats else 0.0
            } for agent in agents]
        }), 200

    return render_template('agents/my_agents.html', agents=agents)


@bp.route('/my-purchases')
@login_required
def my_purchases():
    """View agents purchased by current user."""
    purchases = Purchase.query.filter_by(
        buyer_id=current_user.id,
        is_active=True
    ).order_by(Purchase.purchased_at.desc()).all()

    if request.is_json:
        return jsonify({
            'purchases': [{
                'id': purchase.id,
                'agent_id': purchase.agent.id,
                'agent_name': purchase.agent.name,
                'price_paid': purchase.price_paid,
                'currency': purchase.currency,
                'purchased_at': purchase.purchased_at.isoformat()
            } for purchase in purchases]
        }), 200

    return render_template('agents/my_purchases.html', purchases=purchases)


@bp.route('/upload-package', methods=['GET', 'POST'])
@login_required
def upload_package():
    """Upload a .sagent package file (sellers only)."""
    if not current_user.is_seller:
        flash('You must be a seller to upload agent packages', 'error')
        return redirect(url_for('agents.marketplace'))

    if request.method == 'POST':
        # Check if file part exists
        if 'package' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)

        file = request.files['package']

        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            temp_path = os.path.join(upload_folder, f'temp_{current_user.id}_{filename}')
            file.save(temp_path)

            try:
                # Validate package
                validator = AgentPackageValidator()
                result = validator.validate_package(temp_path)

                if not result['valid']:
                    # Show errors
                    errors_html = '<br>'.join(result['errors'])
                    flash(f'Package validation failed:<br>{errors_html}', 'error')
                    os.remove(temp_path)
                    return redirect(request.url)

                # Extract metadata
                metadata = result['metadata']

                # Create agent (core info)
                agent = Agent(
                    name=metadata['name'],
                    description=metadata['description'],
                    category=metadata['category'],
                    creator_id=current_user.id,
                    is_approved=False  # Requires ethical review
                )
                db.session.add(agent)
                db.session.flush()  # Get agent ID for related records

                # Create agent config (AI settings)
                agent_config = AgentConfig(
                    agent_id=agent.id,
                    system_prompt=metadata['system_prompt'],
                    llm_provider=metadata.get('llm_provider', 'anthropic')
                )
                db.session.add(agent_config)

                # Create agent pricing
                agent_pricing = AgentPricing(
                    agent_id=agent.id,
                    price=float(metadata['price']),
                    currency=metadata['currency']
                )
                db.session.add(agent_pricing)

                # Create agent stats
                agent_stats = AgentStats(
                    agent_id=agent.id,
                    purchase_count=0,
                    average_rating=0.0
                )
                db.session.add(agent_stats)

                # Extract package to permanent location
                extractor = AgentPackageExtractor(upload_folder)
                package_path = extractor.extract_package(temp_path, agent.id)

                # Create agent package record
                agent_package = AgentPackage(
                    agent_id=agent.id,
                    has_package=True,
                    version=metadata.get('version', '1.0.0'),
                    file_path=package_path
                )
                db.session.add(agent_package)

                db.session.commit()

                # Remove temp file
                os.remove(temp_path)

                # Show warnings if any
                if result['warnings']:
                    warnings_html = '<br>'.join(result['warnings'])
                    flash(f'Package uploaded successfully! Warnings:<br>{warnings_html}', 'info')
                else:
                    flash('Package uploaded successfully! It will be reviewed for ethical compliance before being listed.', 'success')

                return redirect(url_for('agents.detail', agent_id=agent.id))

            except Exception as e:
                # Clean up on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                flash(f'Error processing package: {str(e)}', 'error')
                return redirect(request.url)

        else:
            flash('Invalid file type. Please upload a .sagent or .zip file', 'error')
            return redirect(request.url)

    return render_template('agents/upload_package.html')
