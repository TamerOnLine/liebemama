from flask import Blueprint, current_app
from models.models_definitions import db
from routes.auth_utils import admin_only

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/admin/reset_db', methods=['POST'])
@admin_only
def reset_db():
    """Reset the database by dropping and recreating all tables."""
    try:
        db.drop_all()
        db.create_all()
        current_app.logger.info("Database reset by admin.")
        return "All tables have been dropped and recreated.", 200
    except Exception as e:
        current_app.logger.error("Error during database reset", exc_info=True)
        return "An error occurred while resetting the database. Please try again later.", 500


@reset_bp.route('/dev/reset')
def dev_reset():
    """
    Drops all tables and recreates them without authentication.
    Intended for development use only.

    Returns:
        tuple: A success message and HTTP status code 200.
    """
    # WARNING: This should never be used in production!
    try:
        db.drop_all()
        db.create_all()
        current_app.logger.info("Database reset in development mode.")
        return "Database has been reset (development mode).", 200
    except Exception as e:
        current_app.logger.error("Error during database reset in development mode", exc_info=True)
        return "An error occurred while resetting the database. Please try again later.", 500
