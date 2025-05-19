from flask import (
    Blueprint, request, session, current_app,
    render_template, redirect, url_for, flash
)
from models.models_definitions import db, User
from logic.notification_service import create_notification, get_user_notifications
from logic.validation_utils import validate_form
from logic.decorators import log_exceptions
from flask_login import login_user, login_required, current_user, logout_user

user_auth_bp = Blueprint('user_auth', __name__)


@user_auth_bp.route('/set_language/<lang>')
@log_exceptions()
def set_language(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('products.index'))


@user_auth_bp.route('/register', methods=['GET', 'POST'])
@log_exceptions()
def register():
    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'email': {
                'type': 'string',
                'regex': r'^[^@]+@[^@]+\.[^@]+$',
                'required': True
            },
            'username': {
                'type': 'string',
                'minlength': 3,
                'maxlength': 30,
                'required': True
            },
            'password': {
                'type': 'string',
                'minlength': 8,
                'required': True
            },
            'role': {
                'type': 'string',
                'allowed': ['admin', 'merchant', 'customer'],
                'required': False
            }
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])
        if not is_valid:
            flash("There were errors in your registration form.", "error")
            return render_template('auth/register.html', errors=result)

        existing_user = User.query.filter(
            (User.email == result['email']) |
            (User.username == result['username'])
        ).first()

        if existing_user:
            flash("Email or username already in use.", "error")
            return render_template(
                'auth/register.html',
                errors={'username': ['Email or username already in use.']}
            )

        user = User(
            email=result['email'],
            username=result['username'],
            role=result.get('role', 'customer')
        )
        user.set_password(result['password'])
        db.session.add(user)
        db.session.commit()

        flash(f"Welcome {user.username}, you have successfully registered!", "success")
        return redirect(url_for('user_auth.login'))

    return render_template('auth/register.html')


@user_auth_bp.route('/login', methods=['GET', 'POST'])
@log_exceptions()
def login():
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']

        user = User.query.filter(
            (User.email == email_or_username) |
            (User.username == email_or_username)
        ).first()

        if user and user.check_password(password):
            remember = 'remember' in request.form  # يتحقق إذا تم تحديد المربع
            login_user(user, remember=remember)


            flash("Successfully logged in!", "success")

            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'merchant':
                return redirect(url_for('merchant.dashboard'))
            elif user.role == 'customer':
                return redirect(url_for('user_auth.dashboard'))

            return redirect(url_for('products.index'))

        flash("Invalid login credentials. Please try again.", "error")
        return render_template('auth/login.html', error="Invalid login credentials")
        

    return render_template('auth/login.html')


@user_auth_bp.route('/dashboard')
@login_required
@log_exceptions()
def dashboard():
    return render_template('auth/dashboard.html', username=current_user.username)


@user_auth_bp.route('/logout')
@log_exceptions()
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('user_auth.login'))


@user_auth_bp.route('/profile')
@login_required
@log_exceptions()
def profile():
    return render_template('auth/profile.html', user=current_user)



@user_auth_bp.route('/edit', methods=['GET', 'POST'])
@login_required
@log_exceptions()
def edit_profile():
    user = current_user  # يحصل على المستخدم الحالي تلقائيًا

    if request.method == 'POST':
        data = request.form.to_dict()

        schema = {
            'email': {
                'type': 'string',
                'regex': r'^[^@]+@[^@]+\.[^@]+$',
                'required': True
            },
            'username': {
                'type': 'string',
                'minlength': 3,
                'maxlength': 30,
                'required': True
            }
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])

        if not is_valid:
            flash("There were errors in updating your profile.", "error")
            return render_template('auth/edit_profile.html', user=user, errors=result)

        user.username = result['username']
        user.email = result['email']
        db.session.commit()

        flash("Your profile has been updated successfully.", "success")
        return redirect(url_for('user_auth.profile'))

    return render_template('auth/edit_profile.html', user=user)


@user_auth_bp.route('/delete_account', methods=['POST'])
@login_required
@log_exceptions()
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash("Your account has been deleted.", "warning")
    return redirect(url_for('user_auth.register'))

