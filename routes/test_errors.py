import os
from flask import Blueprint, abort, render_template, current_app


test_errors_bp = Blueprint('test_errors', __name__, url_prefix='/test-errors')


def is_dev_mode():
    """
    Check if the current environment is development.

    Returns:
        bool: True if in development mode, else False.
    """
    return current_app.config.get("ENV") == "development"


@test_errors_bp.before_request
def block_if_not_dev():
    """
    Block all non-development requests and log the attempts.

    Raises:
        403: If the environment is not development.
    """
    if not is_dev_mode():
        current_app.logger.warning(
            "Unauthorized access attempt to error testing routes"
        )
        abort(403)


@test_errors_bp.route('/401')
def trigger_401():
    """
    Trigger a 401 Unauthorized error.

    Raises:
        401: Always.
    """
    current_app.logger.info("Triggering 401 Unauthorized error")
    abort(401)


@test_errors_bp.route('/403')
def trigger_403():
    """
    Trigger a 403 Forbidden error.

    Raises:
        403: Always.
    """
    current_app.logger.info("Triggering 403 Forbidden error")
    abort(403)


@test_errors_bp.route('/404')
def trigger_404():
    """
    Trigger a 404 Not Found error.

    Raises:
        404: Always.
    """
    current_app.logger.info("Triggering 404 Not Found error")
    abort(404)


@test_errors_bp.route('/500')
def trigger_500():
    """
    Trigger a 500 Internal Server Error.

    Raises:
        Exception: Always raises a test exception.
    """
    current_app.logger.info("Triggering 500 Internal Server Error")
    raise Exception("Internal Server Error Test")


@test_errors_bp.route('/custom/<int:code>')
def trigger_custom(code):
    """
    Trigger a custom HTTP error code.

    Args:
        code (int): The HTTP error code to trigger.

    Raises:
        abort: With the provided code.
    """
    current_app.logger.info("Triggering custom error %d", code)
    abort(code)
