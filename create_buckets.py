from minio import Minio

# Initialize MinIO client
client = Minio(
    "localhost:9000",
    access_key="minioadmin",  # Change to your access key if different
    secret_key="minio123",    # Change to your secret key if different
    secure=False              # Use True if MinIO uses HTTPS
)

# List of buckets to create
buckets = ["admin-product", "merchant-product", "client-product"]

# Create buckets if they don't exist
for bucket in buckets:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print(f"✅ Created bucket: {bucket}")
    else:
        print(f"✔️ Bucket already exists: {bucket}")

