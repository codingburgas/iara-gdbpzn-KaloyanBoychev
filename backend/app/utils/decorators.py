# app/utils/decorators.py
"""
Custom route decorators for role-based access control.

Usage:
    @app.route('/ops-only')
    @login_required          ← always first
    @ops_required            ← then role check
    def my_view():
        ...

IMPORTANT: @login_required must always come BEFORE the role decorator.
Flask-Login's @login_required redirects unauthenticated users to the
login page. The role decorator assumes the user IS authenticated.
"""

from functools import wraps
from flask import abort
from flask_login import current_user
from app.models.user import UserRole


def ops_required(f):
    """
    Restrict access to Operations Center staff and Admins only.
    Returns HTTP 403 Forbidden for any other role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in (UserRole.OPERATIONS_CENTER, UserRole.ADMIN):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Restrict access to Admins only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != UserRole.ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def firefighter_required(f):
    """Restrict access to Firefighters only (e.g., mobile app views)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in (UserRole.FIREFIGHTER, UserRole.ADMIN):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def ops_or_dispatcher_required(f):
    """
    Allow Operations Center, Dispatchers, and Admins.
    Used for incident creation — dispatchers can log 112 calls,
    ops center can also register incidents from the dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        allowed = (UserRole.OPERATIONS_CENTER, UserRole.DISPATCHER, UserRole.ADMIN)
        if current_user.role not in allowed:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function