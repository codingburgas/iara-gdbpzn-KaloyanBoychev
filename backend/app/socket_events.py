# app/socket_events.py
"""
SocketIO event handlers.

This file is imported once inside create_app() so that all @socketio.on(...)
decorators register themselves with the SocketIO instance.

Room naming convention:
    ops_center        -> joined by all Operations Center / Admin / Dispatcher users
    incident_<id>      -> joined by anyone viewing/working that specific incident
    user_<id>           -> private room for direct-to-user notifications
"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from app import socketio, db
from app.models.message import SOSAlert, SOSAlertStatus
from app.models.user import UserRole


# ── Connection lifecycle ─────────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    """
    Fired automatically whenever a browser tab opens a WebSocket connection.
    We auto-join the user to their private room and, if they are Ops/Admin/
    Dispatcher, to the shared ops_center room.
    """
    if not current_user.is_authenticated:
        return False  # Reject anonymous connections

    join_room(f'user_{current_user.id}')

    if current_user.role in (UserRole.OPERATIONS_CENTER, UserRole.ADMIN, UserRole.DISPATCHER):
        join_room('ops_center')

    print(f'[SocketIO] {current_user.username} connected (sid={request.sid})')


@socketio.on('disconnect')
def handle_disconnect():
    """Fired automatically when a tab closes or loses connection."""
    if current_user.is_authenticated:
        print(f'[SocketIO] {current_user.username} disconnected')


# ── Incident room management ─────────────────────────────────────────────────

@socketio.on('join_incident')
def handle_join_incident(data):
    """
    Client calls this when opening an incident detail page.
    Lets us broadcast chat messages and status changes only to people
    currently viewing that specific incident.

    Expected data: {'incident_id': 5}
    """
    incident_id = data.get('incident_id')
    if incident_id is not None:
        join_room(f'incident_{incident_id}')
        emit('joined_incident', {'incident_id': incident_id})


@socketio.on('leave_incident')
def handle_leave_incident(data):
    """Client calls this when navigating away from an incident page."""
    incident_id = data.get('incident_id')
    if incident_id is not None:
        leave_room(f'incident_{incident_id}')


# ── GPS location updates ─────────────────────────────────────────────────────

@socketio.on('gps_update')
def handle_gps_update(data):
    """
    Fired periodically by a firefighter's mobile browser (e.g. every 15s)
    while they have an active shift. Updates their stored location and
    broadcasts the new position to the Operations Center map.

    Expected data: {'latitude': 42.5048, 'longitude': 27.4626}
    """
    if not current_user.is_authenticated or not current_user.is_firefighter:
        return

    lat = data.get('latitude')
    lng = data.get('longitude')
    if lat is None or lng is None:
        return

    from datetime import datetime
    current_user.last_known_latitude = lat
    current_user.last_known_longitude = lng
    current_user.location_updated_at = datetime.utcnow()
    db.session.commit()

    # Broadcast the new position to anyone watching the ops map
    emit('crew_position_update', {
        'user_id': current_user.id,
        'name': current_user.full_name,
        'latitude': lat,
        'longitude': lng,
    }, room='ops_center')


# ── SOS Alert ─────────────────────────────────────────────────────────────────

@socketio.on('sos_trigger')
def handle_sos_trigger(data):
    """
    Fired when a firefighter taps the "I NEED HELP" button on mobile.
    Persists the alert to the database AND broadcasts it instantly to
    every connected Operations Center browser.

    Expected data: {'latitude': 42.5, 'longitude': 27.4, 'incident_id': 3, 'notes': '...'}
    """
    if not current_user.is_authenticated or not current_user.is_firefighter:
        return

    alert = SOSAlert(
        firefighter_id=current_user.id,
        incident_id=data.get('incident_id'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        notes=data.get('notes'),
        status=SOSAlertStatus.ACTIVE,
    )
    db.session.add(alert)
    db.session.commit()

    # Broadcast to the entire Operations Center room — this is the
    # "every ops screen lights up" moment described in the brief
    emit('sos_alert_received', {
        'alert_id': alert.id,
        'firefighter_id': current_user.id,
        'firefighter_name': current_user.full_name,
        'latitude': alert.latitude,
        'longitude': alert.longitude,
        'incident_id': alert.incident_id,
        'notes': alert.notes,
        'triggered_at': alert.triggered_at.isoformat(),
    }, room='ops_center')

    print(f'[SOS] {current_user.full_name} triggered SOS alert #{alert.id}')


@socketio.on('sos_acknowledge')
def handle_sos_acknowledge(data):
    """
    Fired when an Ops Center user clicks "Acknowledge" on an active SOS.
    Updates the database and notifies the firefighter directly that
    help is coming.

    Expected data: {'alert_id': 7}
    """
    if not current_user.is_authenticated:
        return
    if current_user.role not in (UserRole.OPERATIONS_CENTER, UserRole.ADMIN):
        return

    alert = db.session.get(SOSAlert, data.get('alert_id'))
    if alert is None or alert.status != SOSAlertStatus.ACTIVE:
        return

    alert.acknowledge(current_user.id)
    db.session.commit()

    # Tell every ops screen this alert is now handled (removes it from their UI)
    emit('sos_acknowledged', {
        'alert_id': alert.id,
        'acknowledged_by': current_user.full_name,
    }, room='ops_center')

    # Tell the firefighter directly: "help is on the way"
    emit('sos_response_confirmed', {
        'alert_id': alert.id,
        'acknowledged_by': current_user.full_name,
    }, room=f'user_{alert.firefighter_id}')