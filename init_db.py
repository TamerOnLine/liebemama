# -*- coding: utf-8 -*-
"""
Initializes the database using SQLAlchemy and Flask application context.
This script connects to the PostgreSQL database using the DATABASE_URL
from environment variables, sets up the SQLAlchemy configurations, and
creates all defined tables.
"""

import os

from myapp import create_app
from models.models_definitions import db

# Retrieve PostgreSQL connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
print("DATABASE_URL:", DATABASE_URL)

# Create Flask application
app = create_app()

# Override database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create all tables within the PostgreSQL database
with app.app_context():
    db.create_all()
    print("Tables created successfully in the PostgreSQL database.")
