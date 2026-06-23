# tests/test_user_model.py
"""Unit tests for the User model's authentication helpers."""

from app.models.user import User, UserRole, LeaveStatus


def test_password_hashing_and_verification(db):
    """A correct password should verify; an incorrect one should not."""
    user = User(
        first_name='Maria', last_name='Georgieva',
        username='mgeorgieva', email='m@gdpbzn.bg',
        role=UserRole.OPERATIONS_CENTER
    )
    user.set_password('correct-password')
    db.session.add(user)
    db.session.commit()

    assert user.check_password('correct-password') is True
    assert user.check_password('wrong-password') is False


def test_password_is_never_stored_in_plaintext(db):
    """The raw password must never appear in password_hash."""
    user = User(
        first_name='Ivan', last_name='Petrov',
        username='ipetrov', email='i@gdpbzn.bg',
        role=UserRole.ADMIN
    )
    user.set_password('mysecretpassword')
    assert user.password_hash != 'mysecretpassword'
    assert 'mysecretpassword' not in user.password_hash


def test_role_helper_properties(db):
    """is_admin / is_firefighter / is_ops should match the assigned role."""
    admin = User(first_name='A', last_name='B', username='admin2',
                 email='admin2@gdpbzn.bg', role=UserRole.ADMIN)
    admin.set_password('x')

    firefighter = User(first_name='C', last_name='D', username='ff10',
                       email='ff10@gdpbzn.bg', role=UserRole.FIREFIGHTER)
    firefighter.set_password('x')

    assert admin.is_admin is True
    assert admin.is_firefighter is False

    assert firefighter.is_firefighter is True
    assert firefighter.is_admin is False


def test_full_name_property(db):
    """full_name should combine first and last name with a space."""
    user = User(first_name='Георги', last_name='Иванов', username='gi',
               email='gi@gdpbzn.bg', role=UserRole.FIREFIGHTER)
    assert user.full_name == 'Георги Иванов'


def test_default_leave_status_is_on_duty(db):
    """A newly created user should default to ON_DUTY once persisted."""
    user = User(first_name='New', last_name='User', username='newuser',
               email='new@gdpbzn.bg', role=UserRole.FIREFIGHTER)
    user.set_password('x')
    db.session.add(user)
    db.session.commit()
    assert user.leave_status == LeaveStatus.ON_DUTY

def test_username_must_be_unique(db):
    """Creating two users with the same username should violate the
    unique constraint at the database level."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    user1 = User(first_name='A', last_name='A', username='duplicate',
                email='a@gdpbzn.bg', role=UserRole.FIREFIGHTER)
    user1.set_password('x')
    db.session.add(user1)
    db.session.commit()

    user2 = User(first_name='B', last_name='B', username='duplicate',
                email='b@gdpbzn.bg', role=UserRole.FIREFIGHTER)
    user2.set_password('x')
    db.session.add(user2)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()