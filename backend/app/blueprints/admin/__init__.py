# app/blueprints/admin/__init__.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required

from app import db
from app.models.user import User, UserRole
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.last_name).all()
    roles = [r.value for r in UserRole]
    return render_template('admin/users.html', users=users, roles=roles, title='User Administration')


@admin_bp.route('/users/<int:user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def update_role(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    new_role_value = request.form.get('role')
    try:
        user.role = UserRole(new_role_value)
        db.session.commit()
        flash(f'{user.full_name} is now {user.role.value}.', 'success')
    except ValueError:
        flash('Invalid role.', 'danger')

    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    flash(f'{user.full_name} {status}.', 'info')
    return redirect(url_for('admin.list_users'))