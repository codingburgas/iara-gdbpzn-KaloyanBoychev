# app/blueprints/shifts/__init__.py
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required

from app import db
from app.models.crew import Crew, Shift
from app.models.vehicle import Vehicle, VehicleStatus
from app.utils.decorators import ops_required

shifts_bp = Blueprint(
    'shifts', __name__,
    template_folder='../../templates/shifts'
)


@shifts_bp.route('/')
@login_required
@ops_required
def list_shifts():
    """Show every crew with its current active shift, if any."""
    crews = Crew.query.filter_by(is_active=True).order_by(Crew.name).all()
    available_vehicles = Vehicle.query.filter_by(status=VehicleStatus.AVAILABLE).all()

    return render_template(
        'shifts/list.html',
        crews=crews,
        available_vehicles=available_vehicles,
        title='Shift Management'
    )


@shifts_bp.route('/<int:crew_id>/start', methods=['POST'])
@login_required
@ops_required
def start_shift(crew_id):
    """Start a new shift for a crew, optionally linking a vehicle."""
    crew = db.session.get(Crew, crew_id)
    if crew is None:
        abort(404)

    # Don't allow starting a second active shift for the same crew
    existing = Shift.query.filter_by(crew_id=crew_id, is_active=True).first()
    if existing:
        flash(f'{crew.name} already has an active shift.', 'warning')
        return redirect(url_for('shifts.list_shifts'))

    vehicle_id = request.form.get('vehicle_id', type=int)

    shift = Shift(
        crew_id=crew_id,
        vehicle_id=vehicle_id if vehicle_id else None,
        start_time=datetime.utcnow(),
        is_active=True,
    )
    db.session.add(shift)
    db.session.commit()

    flash(f'Shift started for {crew.name}.', 'success')
    return redirect(url_for('shifts.list_shifts'))


@shifts_bp.route('/<int:shift_id>/end', methods=['POST'])
@login_required
@ops_required
def end_shift(shift_id):
    """End an active shift."""
    shift = db.session.get(Shift, shift_id)
    if shift is None:
        abort(404)

    shift.end_shift()
    db.session.commit()

    flash(f'Shift ended for {shift.crew.name}.', 'info')
    return redirect(url_for('shifts.list_shifts'))