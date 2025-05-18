import os
import getpass
from datetime import datetime

from flask import Flask, render_template, session, request, redirect, url_for
from dotenv import load_dotenv

from models.models_definitions import db, User
from routes import register_routes, register_error_handlers
from config.logging_config import setup_logging
from flask_babel import Babel
from flask_babel import get_locale as babel_get_locale

# تحميل ملف البيئة (للاستخدام مرة واحدة فقط)
load_dotenv()
babel = Babel()


def select_locale():
    return session.get('lang') or request.accept_languages.best_match(['en', 'ar', 'de'])


def create_app():
    app = Flask(__name__)

    # إعدادات عامة
    app.config['TRAP_HTTP_EXCEPTIONS'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # مسار رفع الملفات
    app.config['UPLOAD_FOLDER'] = os.path.join('/tmp', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

    # إعداد قاعدة البيانات من .env
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL not found in .env")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # تهيئة الإضافات
    setup_logging(app)
    babel.init_app(app, locale_selector=select_locale)
    app.jinja_env.globals['get_locale'] = select_locale
    db.init_app(app)

    # تسجيل الراوتات ومعالجات الأخطاء
    register_routes(app)
    register_error_handlers(app)

    return app



app = create_app()


@app.route("/set_language/<lang>")
def set_language(lang):
    session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}


@app.context_processor
def inject_globals():
    return {
        'site_brand': 'منتجي'
    }


@app.context_processor
def inject_unread_notifications():
    from logic.notification_service import get_user_notifications
    role = session.get('role', 'visitor')
    user_id = session.get('user_id')
    notifications = get_user_notifications(role, user_id)
    unread_count = sum(1 for n in notifications if not n.is_read)
    return dict(unread_count=unread_count)


def create_super_admin_if_needed():
    if User.query.filter_by(role='admin').first():
        print("An owner account already exists. No need to create one.")
        return

    print("Creating a Super Admin account")
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        print("This username or email is already in use.")
        return

    password = getpass.getpass("Enter password (input hidden): ").strip()

    admin = User(username=username, email=email, role='admin')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Super Admin account has been created successfully.")


if __name__ == '__main__':
    env_mode = os.getenv('FLASK_ENV', 'development')
    debug_mode = os.getenv('FLASK_DEBUG', '1') == '1'
    port = int(os.getenv('FLASK_PORT', '1705'))

    app = create_app()

    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)

        # ✅ أنشئ الجداول فقط إذا لم تكن موجودة
        if 'settings' not in inspector.get_table_names():
            db.create_all()

        # ✅ بعد وجود الجداول حمّل الإعدادات
        from logic.settings_utils import populate_env_file_settings, load_all_settings
        populate_env_file_settings(".env")
        load_all_settings(app)
        app.secret_key = app.config.get("cv_kay", "fallback-secret")

        # ✅ أنشئ حساب مشرف إذا لم يوجد
        from models.models_definitions import User
        if not User.query.filter_by(role='admin').first():
            from getpass import getpass
            username = input("Super Admin Username: ")
            email = input("Email: ")
            password = getpass("Password: ")
            admin = User(username=username, email=email, role='admin')
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()

    app.run(debug=debug_mode, host='0.0.0.0', port=port)



