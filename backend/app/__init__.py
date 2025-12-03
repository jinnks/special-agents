"""
Special Agents - Ethical AI Agents Marketplace
Built with Flask + gevent for async handling

Copyright (c) 2025 Special Agents
Licensed under MIT License - See LICENSE file for details
"""
import logging
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from decouple import config
from pythonjsonlogger import jsonlogger
from sqlalchemy import text

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app():
    """Application factory pattern"""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Environment detection
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER')

    # Configuration
    app.config['SECRET_KEY'] = config('SECRET_KEY', default='dev-secret-key-change-in-production')

    # Database URL (handle PostgreSQL URLs from Railway/Render)
    database_url = config('DATABASE_URL', default='sqlite:///special_agents.db')
    # Fix postgres:// to postgresql:// (Railway/Heroku compatibility)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # Anthropic API Key
    app.config['ANTHROPIC_API_KEY'] = config('ANTHROPIC_API_KEY', default='')

    # File upload configuration
    app.config['UPLOAD_FOLDER'] = config('UPLOAD_FOLDER', default='uploads/packages')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'sagent', 'zip'}

    # Production logging
    if is_production:
        # JSON logging for production
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        logHandler.setFormatter(formatter)
        app.logger.addHandler(logHandler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Starting Special Agents in PRODUCTION mode")
    else:
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Starting Special Agents in DEVELOPMENT mode")

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
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

    # Health check endpoint (for monitoring)
    @app.route('/health')
    @limiter.exempt
    def health_check():
        """Health check endpoint for monitoring and load balancers"""
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            app.logger.error(f"Database health check failed: {str(e)}")
            db_status = 'unhealthy'
            return jsonify({
                'status': 'unhealthy',
                'database': db_status
            }), 503

        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'version': '1.0.0'
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 error: {error}")
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 error: {error}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        app.logger.warning(f"Rate limit exceeded: {error}")
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if is_production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Create database tables
    with app.app_context():
        db.create_all()

    app.logger.info("Special Agents initialized successfully")
    return app
