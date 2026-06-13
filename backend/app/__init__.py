
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import config

# Extension instances — no app bound yet (App Factory pattern)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name: str = 'default') -> Flask:
    """
    Application Factory.
    Creates and configures a Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Bind extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so Flask-Migrate can detect all tables
    with app.app_context():
        from app.models import (  # noqa: F401
            user, crew, vehicle, incident, task, message
        )

    # Blueprints registered here in Milestone 2
    # from app.blueprints.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    return app