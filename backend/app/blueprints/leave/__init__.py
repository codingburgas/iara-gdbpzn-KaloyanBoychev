# app/blueprints/leave/__init__.py
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models.leave_request import LeaveRequest, LeaveRequestStatus
from app.models.user import LeaveStatus
from app.blueprints.leave.forms import LeaveRequestForm
from app.utils.decorators import ops_required

leave_bp = Blueprint('leave', __name__, template_folder='../../templates/leave')


@leave_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_request():
    """Any logged-in user can request leave for themselves."""
    form = LeaveRequestForm()

    if form.validate_on_submit():
        request_obj = LeaveRequest(
            user_id=current_user.id,
            leave_type=form.leave_type.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data or None,
        )
        db.session.add(request_obj)
        db.session.commit()

        flash('Leave request submitted.', 'success')
        if current_user.is_firefighter:
            return redirect(url_for('operations.mobile_dashboard'))
        return redirect(url_for('operations.dashboard'))

    return render_template('leave/new.html', form=form, title='Request Leave')


@leave_bp.route('/')
@login_required
@ops_required
def list_requests():
    """Ops/Admin: review all leave requests, pending first."""
    pending = LeaveRequest.query.filter_by(status=LeaveRequestStatus.PENDING) \
                                  .order_by(LeaveRequest.created_at.asc()).all()
    reviewed = LeaveRequest.query.filter(
        LeaveRequest.status != LeaveRequestStatus.PENDING
    ).order_by(LeaveRequest.reviewed_at.desc()).limit(20).all()

    return render_template(
        'leave/list.html',
        pending=pending,
        reviewed=reviewed,
        title='Leave Requests'
    )


@leave_bp.route('/<int:request_id>/approve', methods=['POST'])
@login_required
@ops_required
def approve_request(request_id):
    leave_req = db.session.get(LeaveRequest, request_id)
    if leave_req is None:
        abort(404)

    leave_req.status = LeaveRequestStatus.APPROVED
    leave_req.reviewed_by_id = current_user.id
    leave_req.reviewed_at = datetime.utcnow()

    # Reflect approval on the user's current leave status
    if leave_req.leave_type.value == 'sick':
        leave_req.user.leave_status = LeaveStatus.SICK
    else:
        leave_req.user.leave_status = LeaveStatus.ON_LEAVE

    db.session.commit()
    flash(f'Approved leave request for {leave_req.user.full_name}.', 'success')
    return redirect(url_for('leave.list_requests'))


@leave_bp.route('/<int:request_id>/deny', methods=['POST'])
@login_required
@ops_required
def deny_request(request_id):
    leave_req = db.session.get(LeaveRequest, request_id)
    if leave_req is None:
        abort(404)

    leave_req.status = LeaveRequestStatus.DENIED
    leave_req.reviewed_by_id = current_user.id
    leave_req.reviewed_at = datetime.utcnow()
    db.session.commit()

    flash(f'Denied leave request for {leave_req.user.full_name}.', 'info')
    return redirect(url_for('leave.list_requests'))