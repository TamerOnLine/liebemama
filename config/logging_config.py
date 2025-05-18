# config/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    # Create the 'logs' directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Define the log file path
    log_file = os.path.join('logs', 'error.log')

    # Set up a rotating file handler (max size: 100KB, 5 backup files)
    file_handler = RotatingFileHandler(log_file, maxBytes=102400, backupCount=5)
    file_handler.setLevel(logging.ERROR)  # Only log ERROR and above

    # Set up a logging format for the log entries
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)

    # Add the handler to the app's logger if it doesn't already have one
    if not app.logger.handlers:
        app.logger.addHandler(file_handler)

    # Set the log level for the app's logger
    app.logger.setLevel(logging.ERROR)  # Log only ERROR messages and above
