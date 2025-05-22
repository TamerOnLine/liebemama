from minio.error import S3Error
from flask import current_app
from routes.minio_client import get_minio_client, get_minio_bucket
from models.models_definitions import db, AdminLog

def log_admin_action(action, status="success", details=None):
    log = AdminLog(action=action, status=status, details=details)
    db.session.add(log)
    db.session.commit()

def create_bucket_if_not_exists(role=None):
    """
    Creates the appropriate MinIO bucket based on user role.
    If role is None, will use session or default role.

    Args:
        role (str, optional): 'admin', 'merchant', etc.
    """
    client = get_minio_client()
    bucket_name = get_minio_bucket(role)

    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            log_admin_action("Create Bucket", "success", f"Bucket '{bucket_name}' created.")
        else:
            log_admin_action("Create Bucket", "info", f"Bucket '{bucket_name}' already exists.")
    except S3Error as err:
        current_app.logger.error(f"❌ MinIO Error: {err}")
        log_admin_action("Create Bucket", "error", str(err))
        raise  



def delete_bucket(force=False):
    client = get_minio_client()
    bucket_name = get_minio_bucket()

    try:
        deleted_files = []
        if force:
            for obj in client.list_objects(bucket_name, recursive=True):
                client.remove_object(bucket_name, obj.object_name)
                deleted_files.append(obj.object_name)

        client.remove_bucket(bucket_name)
        log_admin_action("Delete Bucket", "success", f"Bucket '{bucket_name}' deleted. Files: {len(deleted_files)}")
    except S3Error as err:
        log_admin_action("Delete Bucket", "error", str(err))