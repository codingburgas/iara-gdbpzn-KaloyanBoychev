# app/blueprints/operations/__init__.py
from flask import Blueprint, render_template
from flask_login import login_required

from app.models.incident import Incident, IncidentStatus
from app.models.crew import Crew
from app.models.user import User, LeaveStatus
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.message import SOSAlert, SOSAlertStatus
from app.utils.decorators import ops_required

operations_bp = Blueprint(
    'operations', __name__,
    template_folder='../../templates/operations'
)


@operations_bp.route('/')
@login_required
def dashboard():
    """
    Main Operations Center dashboard.
    Shows live summary cards and active incidents table.
    Accessible by all logged-in users; full controls visible only to ops/admin.
    """
    # ── Summary statistics ────────────────────────────────────────────────────
    active_incidents = Incident.query.filter(
        Incident.status.notin_([IncidentStatus.RESOLVED, IncidentStatus.CANCELLED])
    ).order_by(Incident.reported_at.desc()).all()

    total_incidents_today = Incident.query.filter(
        Incident.status == IncidentStatus.RESOLVED
    ).count()

    on_duty_count = User.query.filter_by(
        leave_status=LeaveStatus.ON_DUTY
    ).count()

    available_vehicles = Vehicle.query.filter_by(
        status=VehicleStatus.AVAILABLE
    ).count()

    active_sos = SOSAlert.query.filter_by(
        status=SOSAlertStatus.ACTIVE
    ).all()

    pending_count = Incident.query.filter_by(
        status=IncidentStatus.PENDING
    ).count()

    return render_template(
        'operations/dashboard.html',
        active_incidents=active_incidents,
        total_incidents_today=total_incidents_today,
        on_duty_count=on_duty_count,
        available_vehicles=available_vehicles,
        active_sos=active_sos,
        pending_count=pending_count,
        title='Operations Center'
    )