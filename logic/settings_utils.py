import os
from dotenv import dotenv_values
from models.models_definitions import Setting, db

def load_all_settings(app):
    settings = Setting.query.all()
    for setting in settings:
        app.config[setting.key] = setting.value



def populate_all_env_settings():
    """
    Save all environment variables from .env into the settings table,
    unless they already exist.
    """
    for key, value in os.environ.items():
        exists = Setting.query.filter_by(key=key).first()
        if not exists:
            db.session.add(Setting(key=key, value=value))

    db.session.commit()

from dotenv import dotenv_values
from models.models_definitions import Setting, db

def populate_env_file_settings(env_path=".env"):
    """
    Load only the variables defined in the .env file into the settings table.
    """
    env_vars = dotenv_values(env_path)  # ✅ هذا يقرأ فقط ملف .env

    for key, value in env_vars.items():
        if not Setting.query.filter_by(key=key).first():
            db.session.add(Setting(key=key, value=value))

    db.session.commit()

