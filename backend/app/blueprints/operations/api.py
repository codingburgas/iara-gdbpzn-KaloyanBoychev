# app/blueprints/operations/api.py
"""
Lightweight JSON API endpoints used by the mobile frontend
for polling/fallback scenarios alongside SocketIO.
"""

from datetime import datetime
from flask import jsonify
from flask_login import login_required, current_user

from app import db
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.blueprints.operations import operations_bp


@operations_bp.route('/api/crew-positions')
@login_required
def crew_positions():
    """
    Returns the last known GPS position of every on-duty firefighter.
    Used to initially populate the live map on page load
    (SocketIO then keeps it updated after that).
    """
    firefighters = User.query.filter(
        User.role == UserRole.FIREFIGHTER,
        User.last_known_latitude.isnot(None)
    ).all()

    return jsonify([
        {
            'user_id': f.id,
            'name': f.full_name,
            'latitude': f.last_known_latitude,
            'longitude': f.last_known_longitude,
            'updated_at': f.location_updated_at.isoformat() if f.location_updated_at else None,
        }
        for f in firefighters
    ])


@operations_bp.route('/api/vehicle-positions')
@login_required
def vehicle_positions():
    """Returns the last known GPS position of every vehicle."""
    vehicles = Vehicle.query.filter(
        Vehicle.current_latitude.isnot(None)
    ).all()

    return jsonify([
        {
            'vehicle_id': v.id,
            'call_sign': v.call_sign,
            'plate_number': v.plate_number,
            'latitude': v.current_latitude,
            'longitude': v.current_longitude,
            'status': v.status.value,
        }
        for v in vehicles
    ])