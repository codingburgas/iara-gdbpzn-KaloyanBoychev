# app/blueprints/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User, UserRole


class LoginForm(FlaskForm):
    """Form for the /auth/login page."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    """
    Form for /auth/register.
    In production, registration should be admin-only.
    For development/school demo it is open.
    """
    first_name = StringField(
        'First Name',
        validators=[DataRequired(), Length(min=2, max=64)]
    )
    last_name = StringField(
        'Last Name',
        validators=[DataRequired(), Length(min=2, max=64)]
    )
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    badge_number = StringField(
        'Badge Number',
        validators=[Length(max=20)]
    )
    phone = StringField(
        'Phone',
        validators=[Length(max=20)]
    )
    role = SelectField(
        'Role',
        choices=[
            (UserRole.FIREFIGHTER.value, 'Firefighter'),
            (UserRole.DISPATCHER.value, 'Dispatcher'),
            (UserRole.OPERATIONS_CENTER.value, 'Operations Center'),
            (UserRole.ADMIN.value, 'Administrator'),
        ],
        default=UserRole.FIREFIGHTER.value
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, field):
        """Custom validator: username must be unique."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('This username is already taken.')

    def validate_email(self, field):
        """Custom validator: email must be unique."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email is already registered.')

    def validate_badge_number(self, field):
        """Custom validator: badge number must be unique if provided."""
        if field.data and User.query.filter_by(badge_number=field.data).first():
            raise ValidationError('This badge number is already registered.')