# app/blueprints/vehicles/__init__.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required

from app import db
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType
from app.utils.decorators import ops_required

vehicles_bp = Blueprint(
    'vehicles', __name__,
    template_folder='../../templates/vehicles'
)


@vehicles_bp.route('/')
@login_required
@ops_required
def list_vehicles():
    """Show every vehicle as a card with a status-change control."""
    vehicles = Vehicle.query.order_by(Vehicle.call_sign).all()
    statuses = [s.value for s in VehicleStatus]

    return render_template(
        'vehicles/list.html',
        vehicles=vehicles,
        statuses=statuses,
        title='Vehicle Management'
    )


@vehicles_bp.route('/<int:vehicle_id>/update-status', methods=['POST'])
@login_required
@ops_required
def update_status(vehicle_id):
    """Change a vehicle's operational status."""
    vehicle = db.session.get(Vehicle, vehicle_id)
    if vehicle is None:
        abort(404)

    new_status_value = request.form.get('status')
    try:
        new_status = VehicleStatus(new_status_value)
    except ValueError:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('vehicles.list_vehicles'))

    vehicle.status = new_status
    db.session.commit()

    flash(f'{vehicle.call_sign or vehicle.plate_number} marked as {new_status.value.upper()}.', 'success')
    return redirect(url_for('vehicles.list_vehicles'))