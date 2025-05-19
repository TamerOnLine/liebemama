from functools import wraps
from flask import render_template
from logic.error_utils import log_error_to_db

def log_exceptions(default_template="errors/500.html"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log_error_to_db(e)
                return render_template(default_template, error_message=str(e)), 500
        return wrapper
    return decorator
