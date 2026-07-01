# app/blueprints/leave/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from app.models.leave_request import LeaveRequestType


class LeaveRequestForm(FlaskForm):
    leave_type = SelectField(
        'Type',
        choices=[(t.value, t.value.title()) for t in LeaveRequestType],
        validators=[DataRequired()]
    )
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Request')