from myapp import app
from models.models_definitions import db

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Tables have been reset.")
