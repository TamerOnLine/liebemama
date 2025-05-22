#!/bin/bash

# Set MinIO root user and password
export MINIO_ROOT_USER="minioadmin"
export MINIO_ROOT_PASSWORD="minio123"

echo "📁 Creating data directory..."
sudo mkdir -p /data
sudo chown -R $USER:$USER /data

echo "⬇️ Downloading MinIO..."
wget https://dl.min.io/server/minio/release/linux-amd64/minio -O minio
chmod +x minio
sudo mv minio /usr/local/bin/

echo "⚙️ Creating systemd service file for MinIO..."
sudo tee /etc/systemd/system/minio.service > /dev/null <<EOF
[Unit]
Description=MinIO Object Storage
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target

[Service]
User=root
Group=root
Environment="MINIO_ROOT_USER=minioadmin"
Environment="MINIO_ROOT_PASSWORD=minio123"
ExecStart=/usr/local/bin/minio server /data --console-address ":9001" --address ":9000"
Restart=always
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable minio
sudo systemctl start minio

echo "✅ MinIO is now running on port 9000, with console on port 9001"
