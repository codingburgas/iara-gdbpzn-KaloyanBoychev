# tests/test_auth_routes.py
"""Integration tests for the auth blueprint's HTTP routes."""

from app.models.user import User, UserRole


def test_login_page_loads(client):
    """GET /auth/login should return 200 and contain the login form."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Log In' in response.data or b'Username' in response.data


def test_successful_login_redirects(client, db):
    """A valid username/password should log the user in and redirect."""
    user = User(first_name='Test', last_name='User', username='loginuser',
               email='login@gdpbzn.bg', role=UserRole.OPERATIONS_CENTER)
    user.set_password('correctpassword')
    db.session.add(user)
    db.session.commit()

    response = client.post('/auth/login', data={
        'username': 'loginuser',
        'password': 'correctpassword',
    }, follow_redirects=False)

    # A successful login redirects (302) rather than re-rendering the form
    assert response.status_code == 302


def test_failed_login_shows_error(client, db):
    """An incorrect password should NOT log the user in."""
    user = User(first_name='Test', last_name='User', username='wrongpass',
               email='wrong@gdpbzn.bg', role=UserRole.FIREFIGHTER)
    user.set_password('therealpassword')
    db.session.add(user)
    db.session.commit()

    response = client.post('/auth/login', data={
        'username': 'wrongpass',
        'password': 'notthecorrectpassword',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_protected_page_redirects_when_not_logged_in(client):
    """Visiting the dashboard without logging in should redirect to login."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_logout_requires_login(client):
    """Logout route itself requires an active session."""
    response = client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 302  # redirected to login, not logged out