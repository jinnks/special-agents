# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Database models for Special Agents marketplace
Normalized schema for better performance and maintainability
"""
from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for buyers and sellers."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # User profile
    bio = db.Column(db.Text)
    is_seller = db.Column(db.Boolean, default=False)

    # Relationships
    agents = db.relationship('Agent', backref='creator', lazy=True, cascade='all, delete-orphan')
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if provided password matches hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Agent(db.Model):
    """AI Agent model - core information."""
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)

    # Metadata
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Status
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_approved = db.Column(db.Boolean, default=False, index=True)

    # Relationships (1:1 with related tables)
    config = db.relationship('AgentConfig', backref='agent', uselist=False, cascade='all, delete-orphan')
    package = db.relationship('AgentPackage', backref='agent', uselist=False, cascade='all, delete-orphan')
    pricing = db.relationship('AgentPricing', backref='agent', uselist=False, cascade='all, delete-orphan')
    stats = db.relationship('AgentStats', backref='agent', uselist=False, cascade='all, delete-orphan')

    # Many relationships
    purchases = db.relationship('Purchase', backref='agent', lazy=True)
    reviews = db.relationship('Review', backref='agent', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Agent {self.name}>'


class AgentConfig(db.Model):
    """AI configuration for agents - large text fields."""
    __tablename__ = 'agent_config'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False, unique=True, index=True)

    # AI Configuration
    system_prompt = db.Column(db.Text, nullable=False)
    llm_provider = db.Column(db.String(50), nullable=False, default='anthropic')  # 'anthropic', 'openai', etc.

    # Moderation
    approval_notes = db.Column(db.Text)

    def __repr__(self):
        return f'<AgentConfig {self.agent_id}>'


class AgentPackage(db.Model):
    """Package information for .sagent files."""
    __tablename__ = 'agent_package'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False, unique=True, index=True)

    # Package metadata
    has_package = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20))  # e.g., "1.0.0"
    file_path = db.Column(db.String(500))  # Path to extracted package

    def __repr__(self):
        return f'<AgentPackage {self.agent_id}>'


class AgentPricing(db.Model):
    """Pricing information for agents."""
    __tablename__ = 'agent_pricing'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False, unique=True, index=True)

    # Pricing
    price = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(3), default='USD')

    def __repr__(self):
        return f'<AgentPricing {self.agent_id}: {self.price} {self.currency}>'


class AgentStats(db.Model):
    """Statistics for agents - frequently updated."""
    __tablename__ = 'agent_stats'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False, unique=True, index=True)

    # Stats
    purchase_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)

    # Future stats
    # view_count = db.Column(db.Integer, default=0)
    # last_purchased_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<AgentStats {self.agent_id}: {self.purchase_count} purchases, {self.average_rating} rating>'


class Purchase(db.Model):
    """Purchase/Transaction model."""
    __tablename__ = 'purchase'

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)

    # Transaction details
    price_paid = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Access
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Purchase {self.id}: User {self.buyer_id} bought Agent {self.agent_id}>'


class Review(db.Model):
    """Review and rating model for agents."""
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Review content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Moderation
    is_visible = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Review {self.id}: {self.rating} stars for Agent {self.agent_id}>'
