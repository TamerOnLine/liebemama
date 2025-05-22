#!/bin/bash

echo "🛑 Stopping MinIO service if it exists..."
sudo systemctl stop minio 2>/dev/null
sudo systemctl disable minio 2>/dev/null

echo "🧹 Removing minio.service file..."
sudo rm -f /etc/systemd/system/minio.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "��️ Deleting MinIO binary..."
sudo rm -f /usr/local/bin/minio

echo "🗑️ Deleting storage directory /data..."
sudo rm -rf /data

echo "🧯 Removing nginx configuration if exists..."
sudo rm -f /etc/nginx/sites-enabled/files.liebemama.com
sudo rm -f /etc/nginx/sites-available/files.liebemama.com
sudo systemctl reload nginx

echo "✅ Verifying MinIO service has been removed:"
if systemctl status minio &>/dev/null; then
    echo "⚠️ MinIO service still exists!"
else
    echo "✅ MinIO service has been fully removed."
fi

echo "🎉 Cleanup completed successfully!"
