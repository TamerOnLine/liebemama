import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, current_app
from routes.minio_client import get_minio_client
from dotenv import load_dotenv

# تحميل ملف .env
load_dotenv()

def test_minio_connection():
    try:
        client = get_minio_client()
        buckets = client.list_buckets()
        bucket_names = [b.name for b in buckets]
        return {
            "status": "success",
            "message": "Connection to MinIO successful",
            "buckets": bucket_names
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    app = Flask(__name__)

    # تحميل الإعدادات من البيئة إلى config
    app.config["MINIO_ENDPOINT"] = os.getenv("MINIO_ENDPOINT")
    app.config["MINIO_ACCESS_KEY"] = os.getenv("MINIO_ACCESS_KEY")
    app.config["MINIO_SECRET_KEY"] = os.getenv("MINIO_SECRET_KEY")
    app.config["MINIO_USE_HTTPS"] = os.getenv("MINIO_USE_HTTPS", "True") == "True"

    with app.app_context():
        print(test_minio_connection())
