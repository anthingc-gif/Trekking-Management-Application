import os
from flask import Flask
from app.config import config
from app.extensions import db, jwt, cors, cache


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config[config_name])

    # Ensure instance folder exists
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Ensure exports folder exists
    os.makedirs(app.config.get('EXPORT_DIR', 'exports'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.admin import admin_bp
    from app.api.staff import staff_bp
    from app.api.treks import treks_bp
    from app.api.bookings import bookings_bp
    from app.api.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(treks_bp, url_prefix='/api/treks')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(users_bp, url_prefix='/api/user')

    # Create tables and seed admin
    with app.app_context():
        db.create_all()
        from app.seed import seed_admin
        seed_admin()

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token required'}, 401

    return app
