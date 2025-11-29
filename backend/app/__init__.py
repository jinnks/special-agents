"""
Special Agents - Ethical AI Agents Marketplace
Built with Flask + gevent for async handling

Copyright (c) 2025 Special Agents
Licensed under MIT License - See LICENSE file for details
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from decouple import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Configuration
    app.config['SECRET_KEY'] = config('SECRET_KEY', default='dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL', default='sqlite:///special_agents.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Anthropic API Key
    app.config['ANTHROPIC_API_KEY'] = config('ANTHROPIC_API_KEY', default='')

    # File upload configuration
    app.config['UPLOAD_FOLDER'] = config('UPLOAD_FOLDER', default='uploads/packages')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'sagent', 'zip'}

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.routes import main, auth, agents, chat
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(agents.bp)
    app.register_blueprint(chat.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
