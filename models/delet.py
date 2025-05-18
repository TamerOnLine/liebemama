import sys
import os
from flask import Flask
from models.models_definitions import db

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the actual app (adjust the import according to your project structure)
from myapp import app  # Modify this according to your actual project structure

with app.app_context():
    # 1. Extract table names from the database metadata
    tables = db.metadata.tables.keys()
    tables = list(tables)

    # 2. Display numbered list of tables
    print("📋 Current Tables:")
    print("0) Delete all tables")
    for i, table_name in enumerate(tables, start=1):
        print(f"{i}) {table_name}")

    # 3. Ask the user to choose a table to delete or delete all tables
    choice = input("Enter the number of the table you want to delete (or 0 to delete all): ").strip()

    try:
        choice = int(choice)
        if choice == 0:
            # Ask for confirmation to delete all tables
            confirm = input("⚠️ Confirmation: Are you sure you want to delete all tables? (y/n): ")
            if confirm.lower() == 'y':
                db.drop_all()  # Drop all tables from the database
                print("✅ All tables have been deleted.")
            else:
                print("❌ Deletion of all tables was canceled.")
        elif 1 <= choice <= len(tables):
            # Drop the selected table
            table_name = tables[choice - 1]
            db.metadata.tables[table_name].drop(db.engine)
            print(f"✅ Table '{table_name}' has been deleted.")
        else:
            print("❌ Invalid choice. Please select a valid option.")
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")
    except Exception as e:
        # Catch any unexpected errors
        print(f"❌ Error: {e}")
