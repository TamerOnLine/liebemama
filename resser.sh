#!/bin/bash

echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + && find . -type f -name "*.pyc" -delete

echo "Restarting Gunicorn service..."
sudo systemctl restart gunicorn

echo "Showing last 50 lines from Gunicorn logs..."
sudo journalctl -u gunicorn -n 50 --no-pager
