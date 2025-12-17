# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Pytest fixtures and configuration
"""
import pytest
import sys
import os
from unittest.mock import MagicMock

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db as _db
from app.models import User, Agent, AgentConfig, AgentPricing, AgentStats, Purchase, Review


@pytest.fixture(scope='function')
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key-for-testing-only'

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """Create database for testing"""
    with app.app_context():
        yield _db


@pytest.fixture
def user(db):
    """Create a test user"""
    user = User(
        username='testuser',
        email='test@example.com',
        is_seller=False
    )
    user.set_password('Password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def seller(db):
    """Create a test seller"""
    seller = User(
        username='testseller',
        email='seller@example.com',
        is_seller=True
    )
    seller.set_password('Password123')
    db.session.add(seller)
    db.session.commit()
    return seller


@pytest.fixture
def agent(db, seller):
    """Create a test agent"""
    agent = Agent(
        name='Test Agent',
        description='A test agent for testing',
        category='education',
        creator_id=seller.id,
        is_approved=True,
        is_active=True
    )
    db.session.add(agent)
    db.session.flush()

    # Add config
    config = AgentConfig(
        agent_id=agent.id,
        system_prompt='You are a test agent',
        llm_provider='anthropic'
    )
    db.session.add(config)

    # Add pricing
    pricing = AgentPricing(
        agent_id=agent.id,
        price=9.99,
        currency='USD'
    )
    db.session.add(pricing)

    # Add stats
    stats = AgentStats(
        agent_id=agent.id,
        purchase_count=0,
        average_rating=0.0
    )
    db.session.add(stats)

    db.session.commit()
    return agent


@pytest.fixture
def authenticated_client(client, user, app):
    """Create authenticated test client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
    # Store user_id for tests that need it
    client.application.test_user_id = user.id
    return client


@pytest.fixture
def seller_client(client, seller):
    """Create authenticated seller client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(seller.id)
    return client
