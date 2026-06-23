# app/blueprints/operations/__init__.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

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

from app.blueprints.operations import api

@operations_bp.route('/sos-history')
@login_required
@ops_required
def sos_history():
    """Show a full history of all SOS alerts, newest first."""
    from app.models.message import SOSAlert
    alerts = SOSAlert.query.order_by(SOSAlert.triggered_at.desc()).all()
    return render_template(
        'operations/sos_history.html',
        alerts=alerts,
        title='SOS Alert History'
    )

@operations_bp.route('/map')
@login_required
def live_map():
    """Live operations map showing crew and vehicle positions."""
    return render_template('operations/map.html', title='Live Map')

@operations_bp.route('/mobile')
@login_required
def mobile_dashboard():
    """
    Mobile-optimized dashboard for firefighters.
    Shows only incidents assigned to crews this user belongs to,
    plus their own active task list.
    """
    from app.models.incident import Incident, IncidentStatus
    from app.models.task import Task, TaskStatus

    # Get all crew IDs this user belongs to
    my_crew_ids = [c.id for c in current_user.crews]

    my_incidents = Incident.query.filter(
        Incident.assigned_crew_id.in_(my_crew_ids),
        Incident.status.notin_([IncidentStatus.RESOLVED, IncidentStatus.CANCELLED])
    ).order_by(Incident.reported_at.desc()).all() if my_crew_ids else []

    my_tasks = Task.query.filter(
        Task.assigned_crew_id.in_(my_crew_ids),
        Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
    ).order_by(Task.created_at.desc()).all() if my_crew_ids else []

    return render_template(
        'operations/mobile_dashboard.html',
        my_incidents=my_incidents,
        my_tasks=my_tasks,
        title='My Dashboard'
    )