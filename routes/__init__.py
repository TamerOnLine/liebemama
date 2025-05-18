from routes.products import products_bp
from routes.admin_view import admin_bp
from routes.reset import reset_bp
from routes.user_auth import user_auth_bp
from routes.merchant_view import merchant_bp
from routes.notifications_view import notifications_bp
from flask import render_template
from werkzeug.routing import BuildError
from routes.test_errors import test_errors_bp
from routes.product_images_view import product_images_bp
from routes.product_ai import product_ai_bp
# from routes.minio_client import minio_client, MINIO_BUCKET, MINIO_BASE_URL
from routes.admin_settings_view import admin_settings_bp


def register_routes(app):
    """
    Register all application routes using Flask Blueprints.

    This function registers all Blueprints to the Flask app. The Blueprints
    define the different parts of the application, and the routes are registered 
    to handle different sections like products, admin, user authentication, etc.

    Args:
        app (Flask): The Flask application instance.

    Example:
        - products routes will be available under the root URL.
        - admin routes will be prefixed with '/admin'.
    """
    # Registering Blueprints for different parts of the app
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")  # Admin routes have '/admin' prefix
    app.register_blueprint(reset_bp)  # Routes for resetting functionality
    app.register_blueprint(user_auth_bp)  # User authentication routes
    app.register_blueprint(merchant_bp)  # Merchant-related routes
    app.register_blueprint(notifications_bp)  # Routes related to notifications
    app.register_blueprint(test_errors_bp)  # Test routes for error handling (useful in dev mode)
    app.register_blueprint(product_images_bp)
    app.register_blueprint(product_ai_bp)
    app.register_blueprint(admin_settings_bp)


def register_error_handlers(app):
    """
    Register custom error handlers for different HTTP error codes.

    This function handles errors by rendering appropriate templates for each HTTP error
    code (404, 500, etc.) to provide a user-friendly error page. It also handles
    specific errors like unauthorized (401), forbidden (403), and others.

    Args:
        app (Flask): The Flask application instance.
    """
    # Handling internal server errors (500)
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error("❌ 500 Internal Server Error", exc_info=True)
        return render_template("errors/500.html"), 500

    # Handling routing build errors (e.g., invalid URL building)
    @app.errorhandler(BuildError)
    def handle_build_error(e):
        return render_template("errors/500.html"), 500

    # Handling unauthorized errors (401)
    @app.errorhandler(401)
    def unauthorized(e):
        app.logger.warning("🚫 401 Unauthorized", exc_info=True)
        return render_template("errors/401.html"), 401

    # Handling forbidden errors (403)
    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning("⛔ 403 Forbidden", exc_info=True)
        return render_template("errors/403.html"), 403

    # Handling not found errors (404)
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning("🔍 404 Page Not Found", exc_info=True)
        return render_template("errors/404.html"), 404
