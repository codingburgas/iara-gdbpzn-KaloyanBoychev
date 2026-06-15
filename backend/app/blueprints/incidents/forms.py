# app/blueprints/incidents/forms.py
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField,
                     FloatField, SubmitField)
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.models.incident import IncidentType, IncidentPriority
from app.models.crew import Crew


class IncidentForm(FlaskForm):
    """Form for creating and editing an Incident."""

    incident_type = SelectField(
        'Incident Type',
        choices=[(t.value, t.value.replace('_', ' ').title()) for t in IncidentType],
        validators=[DataRequired()]
    )
    priority = SelectField(
        'Priority',
        choices=[(p.value, p.value.upper()) for p in IncidentPriority],
        default=IncidentPriority.MEDIUM.value,
        validators=[DataRequired()]
    )
    address = StringField(
        'Address',
        validators=[DataRequired(), Length(max=255)]
    )
    city = StringField(
        'City',
        default='Бургас',
        validators=[DataRequired(), Length(max=100)]
    )
    latitude = FloatField(
        'Latitude (GPS)',
        validators=[Optional(), NumberRange(min=-90, max=90)]
    )
    longitude = FloatField(
        'Longitude (GPS)',
        validators=[Optional(), NumberRange(min=-180, max=180)]
    )
    caller_name = StringField(
        'Caller Name',
        validators=[Optional(), Length(max=100)]
    )
    caller_phone = StringField(
        'Caller Phone',
        validators=[Optional(), Length(max=20)]
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), Length(max=2000)]
    )
    hazard_notes = TextAreaField(
        'Hazard Notes',
        validators=[Optional(), Length(max=1000)]
    )
    assigned_crew_id = SelectField(
        'Assign Crew',
        coerce=int,
        validators=[Optional()]
    )
    submit = SubmitField('Register Incident')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate crew choices from the database
        crews = Crew.query.filter_by(is_active=True).all()
        self.assigned_crew_id.choices = [(0, '— No crew yet —')] + [
            (c.id, f"{c.name} ({c.station})") for c in crews
        ]