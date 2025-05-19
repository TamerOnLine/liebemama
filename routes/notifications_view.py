from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
from models.models_definitions import db, Notification
from routes.auth_utils import login_required, admin_only
from logic.decorators import log_exceptions

from logic.notification_service import get_user_notifications

admin_settings_bp = Blueprint('admin_settings', __name__, url_prefix='/admin/settings')
notifications_bp = Blueprint('notifications', __name__)


@admin_settings_bp.before_request
@admin_only
@login_required
def restrict_to_admins():
    pass








@notifications_bp.route('/notifications')
@log_exceptions()
def show_notifications():
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')
    notifications = get_user_notifications(role, user_id)
    unread_count = sum(1 for n in notifications if not n.is_read)
    return render_template(
        'shared/notifications.html',
        notifications=notifications,
        unread_count=unread_count
    )


@notifications_bp.route('/notifications/<int:note_id>/hide', methods=['POST'])
@log_exceptions()
def hide_notification(note_id):
    note = Notification.query.get_or_404(note_id)
    check_user_permissions(note)
    note.is_visible = False
    db.session.commit()
    return redirect(url_for('notifications.show_notifications'))


@notifications_bp.route('/notifications/<int:note_id>/restore', methods=['POST'])
@log_exceptions()
def restore_notification(note_id):
    note = Notification.query.get_or_404(note_id)
    check_user_permissions(note)
    note.is_visible = True
    db.session.commit()
    return redirect(url_for('notifications.notification_archive'))


@notifications_bp.route('/notifications/archive')
@log_exceptions()
def notification_archive():
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')
    notifications = Notification.query.filter_by(role=role, is_visible=False)
    if user_id:
        notifications = notifications.filter(
            (Notification.user_id == user_id) | (Notification.user_id.is_(None))
        )
    else:
        notifications = notifications.filter_by(user_id=None)
    notifications = notifications.order_by(Notification.created_at.desc()).all()
    return render_template(
        'shared/notifications_archive.html',
        notifications=notifications
    )


def check_user_permissions(note):
    role = session.get('role')
    user_id = session.get('user_id')
    if note.role != role or (note.user_id and note.user_id != user_id):
        current_app.logger.warning(
            "Unauthorized access attempt by user %s", session.get('username')
        )
        abort(403)
