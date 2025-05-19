from flask import Blueprint, current_app
from models.models_definitions import db
from routes.auth_utils import admin_only
from logic.decorators import log_exceptions

reset_bp = Blueprint('reset', __name__)


@reset_bp.route('/admin/reset_db', methods=['POST'])
@admin_only
@log_exceptions()
def reset_db():
    db.drop_all()
    db.create_all()
    current_app.logger.info("Database reset by admin.")
    return "All tables have been dropped and recreated.", 200


@reset_bp.route('/dev/reset')
@log_exceptions()
def dev_reset():
    db.drop_all()
    db.create_all()
    current_app.logger.info("Database reset in development mode.")
    return "Database has been reset (development mode).", 200
