# app/blueprints/crews/__init__.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required

from app import db
from app.models.crew import Crew
from app.models.user import User, UserRole
from app.utils.decorators import ops_required

crews_bp = Blueprint(
    'crews', __name__,
    template_folder='../../templates/crews'
)


@crews_bp.route('/')
@login_required
@ops_required
def list_crews():
    """
    Show every crew as a card with its current members and an
    'add member' control. Ops/Admin only.
    """
    crews = Crew.query.order_by(Crew.name).all()

    # All firefighters, used to populate each crew's "add member" dropdown
    all_firefighters = User.query.filter_by(role=UserRole.FIREFIGHTER).all()

    return render_template(
        'crews/list.html',
        crews=crews,
        all_firefighters=all_firefighters,
        title='Crew Management'
    )


@crews_bp.route('/<int:crew_id>/add-member', methods=['POST'])
@login_required
@ops_required
def add_member(crew_id):
    """Add a firefighter to a crew's membership list."""
    crew = db.session.get(Crew, crew_id)
    if crew is None:
        abort(404)

    user_id = request.form.get('user_id', type=int)
    if not user_id:
        flash('No firefighter selected.', 'warning')
        return redirect(url_for('crews.list_crews'))

    user = db.session.get(User, user_id)
    if user is None:
        flash('Firefighter not found.', 'danger')
        return redirect(url_for('crews.list_crews'))

    # Avoid adding the same person twice
    if user in crew.members:
        flash(f'{user.full_name} is already in {crew.name}.', 'info')
        return redirect(url_for('crews.list_crews'))

    crew.members.append(user)
    db.session.commit()

    flash(f'{user.full_name} added to {crew.name}.', 'success')
    return redirect(url_for('crews.list_crews'))


@crews_bp.route('/<int:crew_id>/remove-member/<int:user_id>', methods=['POST'])
@login_required
@ops_required
def remove_member(crew_id, user_id):
    """Remove a firefighter from a crew's membership list."""
    crew = db.session.get(Crew, crew_id)
    if crew is None:
        abort(404)

    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    if user in crew.members:
        crew.members.remove(user)
        db.session.commit()
        flash(f'{user.full_name} removed from {crew.name}.', 'info')
    else:
        flash(f'{user.full_name} was not in {crew.name}.', 'warning')

    return redirect(url_for('crews.list_crews'))