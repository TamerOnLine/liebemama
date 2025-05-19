from flask import current_app, session
from minio import Minio


def get_minio_client():
    """
    Initialize and return a MinIO client using app configuration.

    Returns:
        Minio: Configured MinIO client instance.
    """
    return Minio(
        current_app.config["MINIO_ENDPOINT"],
        access_key=current_app.config["MINIO_ACCESS_KEY"],
        secret_key=current_app.config["MINIO_SECRET_KEY"],
        secure=True
    )


def get_minio_bucket(role=None):
    """
    Retrieve the appropriate MinIO bucket based on user role.

    Args:
        role (str, optional): User role. Defaults to session role.

    Returns:
        str: The name of the MinIO bucket.
    """
    if role is None:
        role = session.get("role", "default")

    if role == 'admin':
        return current_app.config.get("MINIO_BUCKET_ADMIN", "admin-product")
    elif role == 'merchant':
        return current_app.config.get("MINIO_BUCKET_MERCHANT", "merchant-product")
    else:
        return current_app.config.get("MINIO_BUCKET", "client-product")


def get_minio_base_url():
    """
    Retrieve the base URL for MinIO from the app configuration.

    Returns:
        str: Base URL for MinIO.
    """
    return current_app.config["MINIO_BASE_URL"]
