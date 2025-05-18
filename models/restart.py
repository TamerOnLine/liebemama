"""
restart.py

Script to manage database table creation for the Flask application.

This script provides two options for interacting with the database:
1. Drop all tables and recreate them (WARNING: This deletes all existing data).
2. Create only the tables that do not already exist (Safe operation).

Note:
    - This script must not be executed in a production environment.
    - It must be run from the project root directory.

Usage:
    Run the script and follow the prompt to choose one of the two options.
"""

import os
import sys
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from myapp import app
from models.models_definitions import db

# Set up logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_production_environment() -> bool:
    """Check if the current environment is production.

    Returns:
        bool: True if in production environment, False otherwise.
    """
    return os.getenv("FLASK_ENV") == "production"

def prompt_user_choice() -> str:
    """Display options to the user and capture their choice.

    Returns:
        str: User's input choice.
    """
    print("Warning: This script interacts with the database.")
    print("Please choose one of the following options:")
    print("1. Drop all tables and recreate them (This will erase all existing data!)")
    print("2. Create tables only if they do not already exist (Safe option)")
    choice = input("Enter your choice (1 or 2): ").strip()
    return choice

def handle_database_operations(choice: str):
    """Handle database operations based on user choice."""
    try:
        with app.app_context():
            if choice == "1":
                db.drop_all()  # Drop all tables
                db.create_all()  # Recreate all tables
                logging.info("All tables have been dropped and recreated successfully.")
            elif choice == "2":
                db.create_all()  # Create only missing tables
                logging.info("Missing tables have been created successfully.")
            else:
                logging.warning("Invalid choice. No action was performed.")
    except Exception as e:
        logging.error(f"An error occurred during database operations: {e}")
        sys.exit(1)

def main():
    """Main function to execute the database operations based on user input."""
    if is_production_environment():
        logging.error("Execution of this script is not allowed in the production environment.")
        sys.exit(1)

    choice = prompt_user_choice()
    if choice in ["1", "2"]:
        handle_database_operations(choice)
    else:
        logging.error("Invalid choice. No action was performed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
