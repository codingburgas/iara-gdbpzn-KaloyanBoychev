# app/blueprints/auth/__init__.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, UserRole
from app.blueprints.auth.forms import LoginForm, RegisterForm

# Blueprint instance — url_prefix set when registered in app factory
auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET:  Render the login form.
    POST: Validate credentials, log the user in, redirect to dashboard.
    """
    if current_user.is_authenticated:
        return redirect(url_for('operations.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('This account has been deactivated. Contact your administrator.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.full_name}.', 'success')

        # Respect the 'next' parameter (e.g. after being redirected from a
        # protected page back to login)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('operations.dashboard'))

    return render_template('auth/login.html', form=form, title='Log In')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET:  Render the registration form.
    POST: Validate, create user, redirect to login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('operations.dashboard'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            badge_number=form.badge_number.data or None,
            phone=form.phone.data or None,
            role=UserRole(form.role.data),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {user.full_name}. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Create Account')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log the current user out and redirect to login."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))