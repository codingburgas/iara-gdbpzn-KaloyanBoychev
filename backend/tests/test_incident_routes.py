# tests/test_incident_routes.py
"""Integration tests for incident creation and role-based access control."""

from app.models.user import User, UserRole
from app.models.incident import Incident


def _login(client, username, password):
    return client.post('/auth/login', data={
        'username': username, 'password': password
    }, follow_redirects=True)


def _make_user(db, username, role, password='testpass123'):
    user = User(
        first_name='Test', last_name=role.value.title(),
        username=username, email=f'{username}@gdpbzn.bg', role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def test_firefighter_cannot_access_new_incident_form(client, db):
    """Firefighters should get 403 Forbidden on the incident creation page."""
    _make_user(db, 'ffuser', UserRole.FIREFIGHTER)
    _login(client, 'ffuser', 'testpass123')

    response = client.get('/incidents/new')
    assert response.status_code == 403


def test_dispatcher_can_access_new_incident_form(client, db):
    """Dispatchers should be allowed to load the incident creation page."""
    _make_user(db, 'dispuser', UserRole.DISPATCHER)
    _login(client, 'dispuser', 'testpass123')

    response = client.get('/incidents/new')
    assert response.status_code == 200


def test_ops_can_create_incident(client, db):
    """A complete, valid POST should create a new Incident row."""
    _make_user(db, 'opsuser', UserRole.OPERATIONS_CENTER)
    _login(client, 'opsuser', 'testpass123')

    response = client.post('/incidents/new', data={
        'incident_type': 'structure_fire',
        'priority': 'high',
        'address': 'Test Street 123',
        'city': 'Бургас',
        'assigned_crew_id': '0',  # "No crew yet" option
    }, follow_redirects=True)

    assert response.status_code == 200
    incident = Incident.query.filter_by(address='Test Street 123').first()
    assert incident is not None
    assert incident.priority.value == 'high'


def test_anonymous_user_cannot_view_incident_list(client):
    """Unauthenticated requests to the incident list should redirect to login."""
    response = client.get('/incidents/', follow_redirects=False)
    assert response.status_code == 302