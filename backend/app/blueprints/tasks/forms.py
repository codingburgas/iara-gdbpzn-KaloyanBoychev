# app/blueprints/tasks/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models.task import TaskType
from app.models.crew import Crew


class TaskForm(FlaskForm):
    """Form for creating a task tied to a specific incident."""

    title = StringField(
        'Task Title',
        validators=[DataRequired(), Length(max=200)]
    )
    task_type = SelectField(
        'Task Type',
        choices=[(t.value, t.value.replace('_', ' ').title()) for t in TaskType],
        validators=[DataRequired()]
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), Length(max=1000)]
    )
    assigned_crew_id = SelectField(
        'Assign To Crew',
        coerce=int,
        validators=[DataRequired(message='Select a crew to assign this task to.')]
    )
    location_notes = StringField(
        'Location Notes',
        validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField('Create Task')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        crews = Crew.query.filter_by(is_active=True).all()
        self.assigned_crew_id.choices = [
            (c.id, f"{c.name} ({c.station})") for c in crews
        ]