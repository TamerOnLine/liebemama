from functools import wraps
from flask import render_template, current_app
from flask_login import current_user

def login_required(f):
    """
    Decorator to ensure the user is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            current_app.logger.warning("Unauthorized access attempt detected.")
            return render_template("errors/401.html"), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_only(f):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🔐 admin_only check → Authenticated: {current_user.is_authenticated}, Role: {getattr(current_user, 'role', '❌')}")
        if not current_user.is_authenticated or current_user.role != 'admin':
            current_app.logger.warning("⛔ Access denied: user is not admin")
            return render_template("errors/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function
