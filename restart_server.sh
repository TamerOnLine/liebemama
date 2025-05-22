#!/bin/bash

echo "🔁 Restarting Gunicorn server..."
sudo systemctl restart gunicorn
echo "✅ Gunicorn restarted successfully."
