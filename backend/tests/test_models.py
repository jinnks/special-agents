# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Unit tests for database models
Fast, isolated tests for model functionality
"""
import pytest
from app.models import User, Agent, AgentConfig, AgentPricing, AgentStats, AgentPackage, Purchase, Review


class TestUserModel:
    """Test User model"""

    def test_create_user(self, db):
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.is_seller is False

    def test_set_password_hashes(self, db):
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password123')

        assert user.password_hash != 'Password123'
        assert len(user.password_hash) > 0

    def test_check_password_correct(self, db):
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password123')

        assert user.check_password('Password123') is True

    def test_check_password_incorrect(self, db):
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password123')

        assert user.check_password('WrongPassword') is False

    def test_user_repr(self, db):
        user = User(username='testuser', email='test@example.com')
        assert 'testuser' in repr(user)

    def test_user_is_seller(self, db):
        seller = User(username='seller', email='seller@example.com', is_seller=True)
        seller.set_password('Password123')
        db.session.add(seller)
        db.session.commit()

        assert seller.is_seller is True


class TestAgentModel:
    """Test Agent model"""

    def test_create_agent(self, db, seller):
        agent = Agent(
            name='Test Agent',
            description='Description',
            category='education',
            creator_id=seller.id
        )
        db.session.add(agent)
        db.session.commit()

        assert agent.id is not None
        assert agent.name == 'Test Agent'
        assert agent.is_approved is False
        assert agent.is_active is True

    def test_agent_repr(self, db, seller):
        agent = Agent(name='Test Agent', description='Desc', category='education', creator_id=seller.id)
        assert 'Test Agent' in repr(agent)

    def test_agent_relationships(self, db, agent):
        assert agent.config is not None
        assert agent.pricing is not None
        assert agent.stats is not None


class TestAgentConfigModel:
    """Test AgentConfig model"""

    def test_create_agent_config(self, db, agent):
        config = agent.config

        assert config.agent_id == agent.id
        assert config.system_prompt == 'You are a test agent'
        assert config.llm_provider == 'anthropic'

    def test_config_repr(self, db, agent):
        assert str(agent.id) in repr(agent.config)


class TestAgentPricingModel:
    """Test AgentPricing model"""

    def test_create_agent_pricing(self, db, agent):
        pricing = agent.pricing

        assert pricing.agent_id == agent.id
        assert pricing.price == 9.99
        assert pricing.currency == 'USD'

    def test_pricing_repr(self, db, agent):
        repr_str = repr(agent.pricing)
        assert str(agent.id) in repr_str
        assert '9.99' in repr_str


class TestAgentStatsModel:
    """Test AgentStats model"""

    def test_create_agent_stats(self, db, agent):
        stats = agent.stats

        assert stats.agent_id == agent.id
        assert stats.purchase_count == 0
        assert stats.average_rating == 0.0

    def test_stats_repr(self, db, agent):
        repr_str = repr(agent.stats)
        assert str(agent.id) in repr_str
        assert '0 purchases' in repr_str


class TestAgentPackageModel:
    """Test AgentPackage model"""

    def test_create_agent_package(self, db, agent):
        package = AgentPackage(
            agent_id=agent.id,
            has_package=True,
            version='1.0.0',
            file_path='/path/to/package'
        )
        db.session.add(package)
        db.session.commit()

        assert package.agent_id == agent.id
        assert package.has_package is True
        assert package.version == '1.0.0'

    def test_package_repr(self, db, agent):
        package = AgentPackage(agent_id=agent.id)
        db.session.add(package)
        db.session.commit()

        assert str(agent.id) in repr(package)


class TestPurchaseModel:
    """Test Purchase model"""

    def test_create_purchase(self, db, user, agent):
        purchase = Purchase(
            buyer_id=user.id,
            agent_id=agent.id,
            price_paid=9.99,
            currency='USD'
        )
        db.session.add(purchase)
        db.session.commit()

        assert purchase.id is not None
        assert purchase.buyer_id == user.id
        assert purchase.agent_id == agent.id
        assert purchase.is_active is True

    def test_purchase_repr(self, db, user, agent):
        purchase = Purchase(
            buyer_id=user.id,
            agent_id=agent.id,
            price_paid=9.99,
            currency='USD'
        )
        db.session.add(purchase)
        db.session.commit()

        repr_str = repr(purchase)
        assert str(user.id) in repr_str
        assert str(agent.id) in repr_str


class TestReviewModel:
    """Test Review model"""

    def test_create_review(self, db, user, agent):
        review = Review(
            agent_id=agent.id,
            reviewer_id=user.id,
            rating=5,
            comment='Great agent!'
        )
        db.session.add(review)
        db.session.commit()

        assert review.id is not None
        assert review.rating == 5
        assert review.comment == 'Great agent!'
        assert review.is_visible is True

    def test_review_repr(self, db, user, agent):
        review = Review(
            agent_id=agent.id,
            reviewer_id=user.id,
            rating=4,
            comment='Good'
        )
        db.session.add(review)
        db.session.commit()

        repr_str = repr(review)
        assert '4 stars' in repr_str
        assert str(agent.id) in repr_str
