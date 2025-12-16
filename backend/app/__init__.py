"""
Special Agents - Ethical AI Agents Marketplace
Built with Flask + gevent for async handling

Copyright (c) 2025 Special Agents
Licensed under MIT License - See LICENSE file for details
"""
import logging
import os
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from decouple import config
from pythonjsonlogger import jsonlogger
from sqlalchemy import text
import secrets

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
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

    # Security Configuration
    app.config['SECRET_KEY'] = config('SECRET_KEY', default=secrets.token_hex(32))
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
    app.config['SESSION_COOKIE_SECURE'] = is_production  # HTTPS only in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour sessions

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
    csrf.init_app(app)
    limiter.init_app(app)

    # CORS configuration - restrictive
    CORS(app,
         origins=config('ALLOWED_ORIGINS', default='http://localhost:5000').split(','),
         supports_credentials=True)

    # Talisman for security headers (only in production)
    if is_production:
        Talisman(app,
                force_https=True,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                content_security_policy={
                    'default-src': "'self'",
                    'script-src': ["'self'", "'unsafe-inline'"],  # Needed for inline scripts
                    'style-src': ["'self'", "'unsafe-inline'"],   # Needed for inline styles
                    'img-src': ["'self'", 'data:', 'https:'],
                    'font-src': ["'self'"],
                    'connect-src': ["'self'"],
                    'frame-ancestors': "'none'",
                },
                frame_options='DENY',
                content_security_policy_nonce_in=['script-src'])

    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'strong'  # Protect against session fixation

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

    # Security headers (enhanced)
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        if is_production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response

    # Request validation
    @app.before_request
    def validate_request():
        # Block requests with suspicious headers
        suspicious_headers = ['x-forwarded-host', 'x-original-url', 'x-rewrite-url']
        for header in suspicious_headers:
            if header in request.headers:
                app.logger.warning(f"Suspicious header detected: {header}")
                return jsonify({'error': 'Invalid request'}), 400

        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.path.startswith('/api/') or request.is_json:
                if request.content_type and 'application/json' not in request.content_type:
                    if 'multipart/form-data' not in request.content_type:
                        app.logger.warning(f"Invalid content type: {request.content_type}")

    # Create database tables
    with app.app_context():
        db.create_all()

    app.logger.info("Special Agents initialized successfully")
    return app
