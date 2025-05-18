from models.models_definitions import db, Notification
from logic.notification_service import create_notification

def hide_old_notifications(product_id, role, type):
    """
    Hide all previous notifications associated with a task.

    Args:
        product_id (int): The product ID associated with the task.
        role (str): The role of the user to hide notifications for.
        type (str): The type of notification to hide.
    """
    Notification.query.filter_by(
        product_id=product_id,
        role=role,
        type=type,
        is_visible=True
    ).update({'is_visible': False})
    db.session.commit()

def push_next_notification(user_id, role, message, type, product_id):
    """
    Create a new notification for the next step in the task.

    Args:
        user_id (int): The ID of the user to send the notification to.
        role (str): The role of the user receiving the notification.
        message (str): The message content of the notification.
        type (str): The type of notification.
        product_id (int): The product ID associated with the task.
    """
    create_notification(
        user_id=user_id,
        role=role,
        message=message,
        type=type,
        product_id=product_id,
        is_visible=True
    )

def advance_notification(
    product_id,
    from_role,
    from_type,
    to_user_id,
    to_role,
    to_type,
    message
):
    """
    Move the notification from one phase to another:
    - Hide old notifications related to the sender.
    - Send a new notification to the receiver.

    Args:
        product_id (int): The product ID associated with the task.
        from_role (str): The role whose old notifications will be hidden.
        from_type (str): The type of old notification.
        to_user_id (int or None): The user to send the new notification to.
        to_role (str): The role of the recipient.
        to_type (str): The type of the new notification.
        message (str): The content of the new notification message.
    """
    # Hide the old notifications linked to the sender's role and type
    hide_old_notifications(product_id, from_role, from_type)

    # Push the next notification for the recipient
    push_next_notification(
        user_id=to_user_id,
        role=to_role,
        message=message,
        type=to_type,
        product_id=product_id
    )
