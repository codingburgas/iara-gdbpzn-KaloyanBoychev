# app/blueprints/incidents/__init__.py
from datetime import datetime
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, abort)
from flask_login import login_required, current_user

from app import db
from app.models.incident import Incident, IncidentStatus, IncidentType, IncidentPriority
from app.models.crew import Crew
from app.blueprints.incidents.forms import IncidentForm
from app.utils.decorators import ops_or_dispatcher_required
from app import socketio
incidents_bp = Blueprint(
    'incidents', __name__,
    template_folder='../../templates/incidents'
)


@incidents_bp.route('/')
@login_required
def list_incidents():
    """
    Show all incidents, newest first.
    Supports optional ?status= filter in the URL.
    Example: /incidents/?status=pending
    """
    status_filter = request.args.get('status')

    query = Incident.query.order_by(Incident.reported_at.desc())

    if status_filter:
        try:
            status_enum = IncidentStatus(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass  # Invalid filter value — ignore and show all

    incidents = query.all()
    statuses = [s.value for s in IncidentStatus]

    return render_template(
        'incidents/list.html',
        incidents=incidents,
        statuses=statuses,
        current_status=status_filter,
        title='Incidents'
    )


@incidents_bp.route('/<int:incident_id>')
@login_required
def detail(incident_id):
    """Show full details for a single incident."""
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)
    return render_template(
        'incidents/detail.html',
        incident=incident,
        title=f'Incident {incident.reference_number or incident.id}'
    )


@incidents_bp.route('/new', methods=['GET', 'POST'])
@login_required
@ops_or_dispatcher_required
def new_incident():
    form = IncidentForm()

    if form.validate_on_submit():
        incident = Incident(
            incident_type=IncidentType(form.incident_type.data),
            priority=IncidentPriority(form.priority.data),
            address=form.address.data,
            city=form.city.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            caller_name=form.caller_name.data or None,
            caller_phone=form.caller_phone.data or None,
            description=form.description.data or None,
            hazard_notes=form.hazard_notes.data or None,
            registered_by_id=current_user.id,
        )

        if form.assigned_crew_id.data and form.assigned_crew_id.data != 0:
            incident.assigned_crew_id = form.assigned_crew_id.data
            incident.status = IncidentStatus.DISPATCHED
            incident.dispatched_at = datetime.utcnow()

        db.session.add(incident)
        db.session.flush()

        incident.reference_number = incident.generate_reference()
        db.session.commit()

        # ── Notify assigned crew in real time ─────────────────────────────────
        if incident.assigned_crew_id:
            crew = db.session.get(Crew, incident.assigned_crew_id)
            if crew:
                for member in crew.members:
                    socketio.emit('new_incident_assigned', {
                        'incident_id': incident.id,
                        'reference_number': incident.reference_number,
                        'incident_type': incident.incident_type.value,
                        'priority': incident.priority.value,
                        'address': incident.address,
                        'city': incident.city,
                        'latitude': incident.latitude,
                        'longitude': incident.longitude,
                        'hazard_notes': incident.hazard_notes,
                    }, room=f'user_{member.id}')

        flash(f'Incident {incident.reference_number} registered successfully.', 'success')
        return redirect(url_for('incidents.detail', incident_id=incident.id))

    return render_template('incidents/new.html', form=form, title='New Incident')


@incidents_bp.route('/<int:incident_id>/update-status', methods=['POST'])
@login_required
@ops_or_dispatcher_required
def update_status(incident_id):
    """
    Quick status update via a POST form button on the detail page.
    Expects a 'status' field in the form data.
    """
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)

    new_status_value = request.form.get('status')
    try:
        new_status = IncidentStatus(new_status_value)
    except ValueError:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('incidents.detail', incident_id=incident_id))

    # Update timestamp fields based on the transition
    if new_status == IncidentStatus.ON_SCENE and not incident.on_scene_at:
        incident.on_scene_at = datetime.utcnow()
    elif new_status == IncidentStatus.RESOLVED and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()
    elif new_status == IncidentStatus.DISPATCHED and not incident.dispatched_at:
        incident.dispatched_at = datetime.utcnow()

    incident.status = new_status
    db.session.commit()
    flash(f'Status updated to {new_status.value.upper()}.', 'success')
    return redirect(url_for('incidents.detail', incident_id=incident_id))