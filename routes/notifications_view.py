from flask import Blueprint, session, request, render_template, redirect, url_for, abort, current_app
from models.models_definitions import db, Notification
from logic.notification_service import get_user_notifications

notifications_bp = Blueprint('notifications', __name__)

def check_user_permissions(note):
    """Helper function to check if the current user has permission to modify the notification."""
    role = session.get('role')
    user_id = session.get('user_id')

    if note.role != role or (note.user_id and note.user_id != user_id):
        current_app.logger.warning(f"Unauthorized access attempt by user {session.get('username')}")
        abort(403)

@notifications_bp.route('/notifications')
def show_notifications():
    """Show a list of notifications for the current user."""
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
def hide_notification(note_id):
    """Hide a specific notification."""
    note = Notification.query.get_or_404(note_id)

    # Check if the user has permission to hide this notification
    check_user_permissions(note)

    note.is_visible = False
    db.session.commit()
    return redirect(url_for('notifications.show_notifications'))


@notifications_bp.route('/notifications/<int:note_id>/restore', methods=['POST'])
def restore_notification(note_id):
    """Restore a previously hidden notification."""
    note = Notification.query.get_or_404(note_id)

    # Check if the user has permission to restore this notification
    check_user_permissions(note)

    note.is_visible = True
    db.session.commit()
    return redirect(url_for('notifications.notification_archive'))


@notifications_bp.route('/notifications/archive')
def notification_archive():
    """Show the archived notifications (hidden ones)."""
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')

    notifications = Notification.query.filter_by(role=role, is_visible=False)

    if user_id:
        notifications = notifications.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
    else:
        notifications = notifications.filter_by(user_id=None)

    notifications = notifications.order_by(Notification.created_at.desc()).all()

    return render_template('shared/notifications_archive.html', notifications=notifications)
