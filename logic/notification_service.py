from models.models_definitions import db, Notification

def create_notification(user_id, role, message, type="info", product_id=None, order_id=None, is_visible=True):
    """
    Create and save a new notification.

    Args:
        user_id (int or None): The target user's ID, or None for global notifications
        role (str): The role of the user ('admin', 'merchant', 'customer', 'visitor')
        message (str): The content of the notification
        type (str): Type of notification ('info', 'success', 'error', etc.)
        product_id (int or None): Optional related product ID (defaults to None)
        order_id (int or None): Optional related order ID (defaults to None)
        is_visible (bool): Should the notification be shown in the interface (defaults to True)

    """
    # Create a new notification instance
    notification = Notification(
        user_id=user_id,
        role=role,
        message=message,
        type=type,
        product_id=product_id,
        order_id=order_id,
        is_visible=is_visible
    )

    # Add the notification to the session and commit to save it
    db.session.add(notification)
    db.session.commit()

def get_user_notifications(role, user_id=None):
    """
    Return a list of visible notifications for a user based on role and user_id.

    Args:
        role (str): 'admin', 'merchant', 'customer', 'visitor'
        user_id (int or None): if provided, returns both user-specific and public notifications

    Returns:
        list[Notification]: A list of Notification objects, ordered by creation date (most recent first)
    """
    # Start the query to filter notifications by role and visibility
    query = Notification.query.filter_by(role=role, is_visible=True)

    # If a user_id is provided, return notifications for the user or global notifications
    if user_id:
        query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
    else:
        # If no user_id is provided, only return global notifications
        query = query.filter_by(user_id=None)

    # Order notifications by the creation date, most recent first
    return query.order_by(Notification.created_at.desc()).all()
