# app/blueprints/tasks/__init__.py
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app import db, socketio
from app.models.task import Task, TaskType, TaskStatus
from app.models.incident import Incident
from app.models.crew import Crew
from app.blueprints.tasks.forms import TaskForm
from app.utils.decorators import ops_or_dispatcher_required

tasks_bp = Blueprint(
    'tasks', __name__,
    template_folder='../../templates/tasks'
)


@tasks_bp.route('/incident/<int:incident_id>/new', methods=['GET', 'POST'])
@login_required
@ops_or_dispatcher_required
def new_task(incident_id):
    """Create a new task tied to a specific incident."""
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)

    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data or None,
            task_type=TaskType(form.task_type.data),
            location_notes=form.location_notes.data or None,
            incident_id=incident.id,
            assigned_crew_id=form.assigned_crew_id.data,
            created_by_id=current_user.id,
        )
        db.session.add(task)
        db.session.commit()

        # ── Notify assigned crew in real time (same pattern as incidents) ────
        crew = db.session.get(Crew, task.assigned_crew_id)
        if crew:
            for member in crew.members:
                socketio.emit('new_task_assigned', {
                    'task_id': task.id,
                    'title': task.title,
                    'task_type': task.task_type.value,
                    'incident_id': incident.id,
                    'incident_reference': incident.reference_number,
                }, room=f'user_{member.id}')

        flash(f'Task "{task.title}" created and assigned to {crew.name if crew else "crew"}.', 'success')
        return redirect(url_for('incidents.detail', incident_id=incident.id))

    return render_template(
        'tasks/new.html',
        form=form,
        incident=incident,
        title='New Task'
    )


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@ops_or_dispatcher_required
def edit_task(task_id):
    """Edit an existing task's details / assignment."""
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    form = TaskForm()

    if request.method == 'GET':
        # Pre-fill the form with the task's current values
        form.title.data = task.title
        form.task_type.data = task.task_type.value
        form.description.data = task.description
        form.location_notes.data = task.location_notes
        form.assigned_crew_id.data = task.assigned_crew_id or 0

    if form.validate_on_submit():
        previous_crew_id = task.assigned_crew_id

        task.title = form.title.data
        task.task_type = TaskType(form.task_type.data)
        task.description = form.description.data or None
        task.location_notes = form.location_notes.data or None
        task.assigned_crew_id = form.assigned_crew_id.data

        db.session.commit()

        # Notify the newly assigned crew if the assignment changed
        if task.assigned_crew_id != previous_crew_id:
            crew = db.session.get(Crew, task.assigned_crew_id)
            if crew:
                for member in crew.members:
                    socketio.emit('new_task_assigned', {
                        'task_id': task.id,
                        'title': task.title,
                        'task_type': task.task_type.value,
                        'incident_id': task.incident_id,
                        'incident_reference': task.incident.reference_number,
                    }, room=f'user_{member.id}')

        flash(f'Task "{task.title}" updated.', 'success')
        return redirect(url_for('incidents.detail', incident_id=task.incident_id))

    return render_template(
        'tasks/edit.html',
        form=form,
        task=task,
        incident=task.incident,
        title='Edit Task'
    )


@tasks_bp.route('/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_status(task_id):
    """
    Update a task's status. Allowed for ops/admin/dispatcher (full control)
    AND for firefighters who belong to the assigned crew (can self-manage
    their own task progress).
    """
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    # Permission check: ops/admin/dispatcher OR a member of the assigned crew
    is_privileged = current_user.role.value in ('ops', 'admin', 'dispatcher')
    is_crew_member = (
        task.assigned_crew and
        current_user in task.assigned_crew.members
    )
    if not (is_privileged or is_crew_member):
        abort(403)

    new_status_value = request.form.get('status')
    try:
        new_status = TaskStatus(new_status_value)
    except ValueError:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('incidents.detail', incident_id=task.incident_id))

    task.status = new_status
    if new_status == TaskStatus.COMPLETED:
        task.completed_at = datetime.utcnow()

    db.session.commit()
    flash(f'Task "{task.title}" marked as {new_status.value.upper()}.', 'success')
    return redirect(url_for('incidents.detail', incident_id=task.incident_id))

@tasks_bp.route('/')
@login_required
def list_all_tasks():
    """
    Show all tasks. Ops/admin/dispatcher see everything; firefighters
    see only tasks assigned to crews they belong to.
    """
    if current_user.role.value in ('ops', 'admin', 'dispatcher'):
        tasks = Task.query.order_by(Task.created_at.desc()).all()
    else:
        my_crew_ids = [c.id for c in current_user.crews]
        tasks = Task.query.filter(Task.assigned_crew_id.in_(my_crew_ids)) \
                          .order_by(Task.created_at.desc()).all() if my_crew_ids else []

    return render_template('tasks/list.html', tasks=tasks, title='All Tasks')