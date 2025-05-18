from functools import wraps
from flask import session, redirect, url_for, render_template, abort, current_app
from logic.notification_service import create_notification, get_user_notifications

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is authenticated (has a valid user_id in the session)
        if not session.get('user_id'):
            current_app.logger.warning(f"Unauthorized access attempt detected.")
            return render_template("errors/401.html"), 401  # Custom 401 error page
        return f(*args, **kwargs)
    return decorated_function


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is an admin
        if session.get('role') != 'admin':
            current_app.logger.warning(f"Access denied: Non-admin user attempted to access admin area.")
            return render_template("errors/403.html"), 403  # Custom 403 error page
        return f(*args, **kwargs)
    return decorated_function
