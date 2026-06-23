# tests/conftest.py
"""
Shared pytest fixtures for the entire test suite.
Every test gets a completely fresh, isolated in-memory SQLite database —
nothing here ever touches your real development database.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app, db as _db

import pytest
from app import create_app, db as _db


class TestConfig:
    """Configuration used only during test runs."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for simpler form posts


@pytest.fixture
def app():
    """Creates a Flask app configured for testing, with a fresh in-memory DB."""
    flask_app = create_app('default')
    flask_app.config.from_object(TestConfig)

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A Flask test client — simulates HTTP requests without a real server."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Direct database access within a test, scoped to the app context."""
    return _db


@pytest.fixture
def sample_user(db):
    """Creates and returns one saved firefighter user for tests to reuse."""
    from app.models.user import User, UserRole

    user = User(
        first_name='Test', last_name='Firefighter',
        username='testff', email='testff@gdpbzn.bg',
        role=UserRole.FIREFIGHTER
    )
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user