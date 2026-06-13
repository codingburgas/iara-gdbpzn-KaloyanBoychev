
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-CHANGE-IN-PROD')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///gdpbzn.db'
    )


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True   # prints every SQL query to console


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}