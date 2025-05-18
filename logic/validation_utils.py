import re
from cerberus import Validator
import bleach


def sanitize_text_fields(data, fields):
    """
    Sanitize specified text fields in the provided data dictionary to prevent XSS attacks.

    Args:
        data (dict): The dictionary containing data to sanitize.
        fields (list): The list of field names to sanitize.

    Returns:
        dict: The sanitized data dictionary.
    """
    for field in fields:
        if field in data:
            data[field] = bleach.clean(data[field])
    return data


def validate_form(data, schema, sanitize_fields=None):
    """
    Validate form data against a schema and optionally sanitize specified fields.

    Args:
        data (dict): The dictionary containing form data to validate.
        schema (dict): The schema to validate the data against.
        sanitize_fields (list, optional): A list of field names to sanitize before validation.

    Returns:
        tuple: A tuple where the first element is a boolean indicating success, 
               and the second element contains validation errors (if any).
    """
    if sanitize_fields:
        data = sanitize_text_fields(data, sanitize_fields)

    v = Validator(schema)

    if not v.validate(data):
        return False, v.errors
    return True, v.document


def validate_email(email):
    """
    Validate email format using a regular expression.

    Args:
        email (str): The email string to validate.

    Returns:
        bool: True if the email format is valid, otherwise False.
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def validate_password(password, min_length=8):
    """
    Validate password length.

    Args:
        password (str): The password string to validate.
        min_length (int): The minimum acceptable password length.

    Returns:
        bool: True if the password meets the minimum length requirement, otherwise False.
    """
    return len(password) >= min_length


def sanitize_text(text):
    """
    Sanitize a single text field to prevent XSS attacks.

    Args:
        text (str): The text to sanitize.

    Returns:
        str: The sanitized text.
    """
    return bleach.clean(text)


def validate_price(price):
    """
    Validate if the price is a non-negative number.

    Args:
        price (str): The price to validate.

    Returns:
        bool: True if the price is a non-negative float, otherwise False.
    """
    try:
        value = float(price)
        return value >= 0
    except ValueError:
        return False


def coerce_price(value):
    """
    Coerce price input to float, replacing commas with dots.

    Args:
        value (str): The price input value.

    Returns:
        float: Parsed float value or original if invalid.
    """
    try:
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)
    except (ValueError, TypeError):
        return value  # Let validator fail later if invalid


import bleach

def sanitize_rich_text(html):
    """
    Sanitize HTML input to allow safe formatting while preventing XSS attacks.
    """
    allowed_tags = [
        'p', 'br', 'ul', 'ol', 'li', 'strong', 'em', 'b', 'i', 'u',
        'a', 'span', 'div', 'blockquote', 'hr', 'table', 'tr', 'td',
        'th', 'thead', 'tbody', 'h1', 'h2', 'h3'
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        'span': ['style'],
        'div': ['style'],
        '*': ['style']
    }

    return bleach.clean(html or '', tags=allowed_tags, attributes=allowed_attrs, strip=True)
