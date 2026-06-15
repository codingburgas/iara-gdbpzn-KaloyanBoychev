# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import config
from flask_wtf.csrf import CSRFProtect
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Bind extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Import models for Flask-Migrate
        from app.models import user, crew, vehicle, incident, task, message  # noqa: F401

        # ── Register Blueprints ───────────────────────────────────────────────
        from app.blueprints.auth import auth_bp
        from app.blueprints.incidents import incidents_bp
        from app.blueprints.operations import operations_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(incidents_bp, url_prefix='/incidents')
        app.register_blueprint(operations_bp, url_prefix='/')

    return app