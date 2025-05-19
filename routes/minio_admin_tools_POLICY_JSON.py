from minio.error import S3Error
from routes.minio_client import get_minio_client, get_minio_bucket
from models.models_definitions import db, AdminLog


def log_admin_action(action, status="success", details=None):
    """
    Log an administrative action to the database.

    Args:
        action (str): Description of the action performed.
        status (str): Status of the action (default is "success").
        details (str, optional): Additional details or error messages.
    """
    log = AdminLog(action=action, status=status, details=details)
    db.session.add(log)
    db.session.commit()


def create_bucket_if_not_exists():
    """
    Create a MinIO bucket if it does not already exist.

    Logs the action regardless of whether the bucket was created or already exists.
    """
    client = get_minio_client()
    bucket_name = get_minio_bucket()

    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            log_admin_action(
                "Create Bucket", "success",
                f"Bucket '{bucket_name}' created."
            )
        else:
            log_admin_action(
                "Create Bucket", "success",
                f"Bucket '{bucket_name}' already existed."
            )
    except S3Error as err:
        log_admin_action("Create Bucket", "error", str(err))


def delete_bucket(force=False):
    """
    Delete a MinIO bucket, optionally removing all contained objects.

    Args:
        force (bool): If True, delete all files before removing the bucket.
    """
    client = get_minio_client()
    bucket_name = get_minio_bucket()

    try:
        deleted_files = []
        if force:
            for obj in client.list_objects(bucket_name, recursive=True):
                client.remove_object(bucket_name, obj.object_name)
                deleted_files.append(obj.object_name)

        client.remove_bucket(bucket_name)
        log_admin_action(
            "Delete Bucket", "success",
            f"Bucket '{bucket_name}' deleted. Files: {len(deleted_files)}"
        )
    except S3Error as err:
        log_admin_action("Delete Bucket", "error", str(err))
