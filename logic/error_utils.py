import traceback
from flask import request, session
from models.models_definitions import ErrorLog, db

def log_error_to_db(e):
    tb = traceback.format_exc()
    error_log = ErrorLog(
        endpoint=request.path,
        method=request.method,
        user_id=session.get("user_id"),
        role=session.get("role"),
        error_type=type(e).__name__,
        message=str(e),
        traceback_text=tb
    )
    db.session.add(error_log)
    db.session.commit()
