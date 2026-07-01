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
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.task import Task

incidents_bp = Blueprint(
    'incidents', __name__,
    template_folder='../../templates/incidents'
)


@incidents_bp.route('/')
@login_required
def list_incidents():
    status_filter = request.args.get('status')
    search_query = request.args.get('q', '').strip()
    type_filter = request.args.get('type')

    query = Incident.query.order_by(Incident.reported_at.desc())

    if status_filter:
        try:
            query = query.filter_by(status=IncidentStatus(status_filter))
        except ValueError:
            pass

    if type_filter:
        try:
            query = query.filter_by(incident_type=IncidentType(type_filter))
        except ValueError:
            pass

    if search_query:
        query = query.filter(
            db.or_(
                Incident.address.ilike(f'%{search_query}%'),
                Incident.reference_number.ilike(f'%{search_query}%'),
                Incident.city.ilike(f'%{search_query}%'),
            )
        )

    incidents = query.all()
    statuses = [s.value for s in IncidentStatus]
    types = [t.value for t in IncidentType]

    return render_template(
        'incidents/list.html',
        incidents=incidents,
        statuses=statuses,
        types=types,
        current_status=status_filter,
        current_type=type_filter,
        search_query=search_query,
        title='Incidents'
    )


from app.utils.message_templates import QUICK_MESSAGE_TEMPLATES

@incidents_bp.route('/<int:incident_id>')
@login_required
def detail(incident_id):
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)
    tasks = incident.tasks.order_by(Task.created_at.desc()).all()
    return render_template(
        'incidents/detail.html',
        incident=incident,
        tasks=tasks,
        quick_templates=QUICK_MESSAGE_TEMPLATES,
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

        if form.assigned_vehicle_id.data and form.assigned_vehicle_id.data != 0:
            incident.assigned_vehicle_id = form.assigned_vehicle_id.data
            vehicle = db.session.get(Vehicle, form.assigned_vehicle_id.data)
            if vehicle:
                vehicle.status = VehicleStatus.DEPLOYED

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

@incidents_bp.route('/<int:incident_id>/edit', methods=['GET', 'POST'])
@login_required
@ops_or_dispatcher_required
def edit_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)

    form = IncidentForm(obj=incident)

    if request.method == 'GET':
        # Pre-fill the form with existing values
        form.incident_type.data = incident.incident_type.value
        form.priority.data = incident.priority.value
        form.address.data = incident.address
        form.city.data = incident.city
        form.latitude.data = incident.latitude
        form.longitude.data = incident.longitude
        form.caller_name.data = incident.caller_name
        form.caller_phone.data = incident.caller_phone
        form.description.data = incident.description
        form.hazard_notes.data = incident.hazard_notes
        form.assigned_crew_id.data = incident.assigned_crew_id or 0

    if form.validate_on_submit():
        incident.incident_type = IncidentType(form.incident_type.data)
        incident.priority = IncidentPriority(form.priority.data)
        incident.address = form.address.data
        incident.city = form.city.data
        incident.latitude = form.latitude.data
        incident.longitude = form.longitude.data
        incident.caller_name = form.caller_name.data or None
        incident.caller_phone = form.caller_phone.data or None
        incident.description = form.description.data or None
        incident.hazard_notes = form.hazard_notes.data or None

        if form.assigned_crew_id.data and form.assigned_crew_id.data != 0:
            incident.assigned_crew_id = form.assigned_crew_id.data

        db.session.commit()
        flash('Incident updated.', 'success')
        return redirect(url_for('incidents.detail', incident_id=incident.id))

    return render_template('incidents/edit.html', form=form, incident=incident, title='Edit Incident')