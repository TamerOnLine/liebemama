import os
import uuid
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, current_app, flash, abort
)
from werkzeug.utils import secure_filename

from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url
from models.models_definitions import Product, db
from routes.auth_utils import login_required, admin_only
from flask_login import current_user
from logic.notification_service import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import validate_form
from routes.minio_admin_tools import create_bucket_if_not_exists, delete_bucket
from logic.decorators import log_exceptions


admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/')
@admin_only
@login_required
@log_exceptions()
def admin_dashboard():
    print(f"👤 current_user: {current_user}")
    print(f"🔐 authenticated: {current_user.is_authenticated}")
    print(f"🎭 role: {getattr(current_user, 'role', '❌ role missing')}")
    return render_template('admin/dashboard.html')



@admin_bp.route('/products')
@admin_only
@login_required
@log_exceptions()
def admin_products():
    products = Product.query.all()
    return render_template('admin/admin_products.html', products=products)


@admin_bp.route('/add', methods=['GET', 'POST'])
@admin_only
@login_required
@log_exceptions()
def admin_add_product():
    if request.method == 'POST':
        from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
        from models.models_definitions import ProductImage

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        data = request.form.to_dict()
        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])
        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template(
                'admin/add_product.html', errors=result,
                tinymce_api_key=os.getenv('TINYMCE_API_KEY')
            ), 400

        try:
            sequence = Product.query.count() + 1
            product = Product(
                name=result['name'],
                price=result['price'],
                description=result.get('description'),
                specs=result.get('specs'),
                merchant_id=current_user.id  # استخدام current_user هنا
            )
            product.generate_code(sequence)
            db.session.add(product)
            db.session.flush()

            files = request.files.getlist('images')
            for index, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    folder = f"products/admin/{current_user.id}/product_{product.id}"
                    unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

                    image_data = file.read()
                    file.stream.seek(0)

                    minio_client = get_minio_client()
                    MINIO_BUCKET = get_minio_bucket()
                    MINIO_BASE_URL = get_minio_base_url()

                    minio_client.put_object(
                        MINIO_BUCKET,
                        unique_filename,
                        file.stream,
                        length=len(image_data),
                        part_size=10 * 1024 * 1024,
                        content_type=file.content_type
                    )

                    image_url = MINIO_BASE_URL + unique_filename
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_main=(index == 0)
                    )
                    db.session.add(product_image)

            db.session.commit()
            return redirect(url_for('admin.admin_dashboard'))

        except Exception:
            db.session.rollback()
            current_app.logger.exception("Error adding product")
            return "An unexpected error occurred. Please try again later.", 500

    return render_template(
        'admin/add_product.html',
        tinymce_api_key=os.getenv('TINYMCE_API_KEY')
    )


@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_only
@login_required
@log_exceptions()
def edit_product(product_id):
    from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        data = request.form.to_dict()
        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])
        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template('admin/edit_product.html', product=product, errors=result)

        product.name = result['name']
        product.price = result['price']
        product.description = result.get('description')
        product.specs = result.get('specs')

        db.session.commit()
        flash("Product updated successfully", "success")
        return redirect(url_for('admin.admin_products'))

    return render_template('admin/edit_product.html', product=product)


@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@admin_only
@login_required
@log_exceptions()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully", "success")
    return redirect(url_for('admin.admin_products'))


@admin_bp.route('/approve/<int:product_id>', methods=['POST'])
@admin_only
@login_required
@log_exceptions()
def approve_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_approved = True
    db.session.commit()
    flash("Product approved successfully", "success")
    return redirect(url_for('admin.admin_products'))


@admin_bp.route('/system-links')
@admin_only
@login_required
@log_exceptions()
def system_links():
    return render_template('admin/system_links.html')


@admin_bp.route('/minio-logs')
@admin_only
@login_required
@log_exceptions()
def minio_logs():
    return render_template('admin/minio_logs.html')


@admin_bp.route('/create-minio-bucket', methods=['POST'], endpoint='create_minio_bucket')
@admin_only
@login_required
@log_exceptions()
def create_minio_bucket():
    create_bucket_if_not_exists()
    flash("✅ Bucket created or already exists.", "success")
    return redirect(url_for('admin.system_links'))


@admin_bp.route('/delete-minio-bucket', methods=['POST'])
@admin_only
@login_required
@log_exceptions()
def delete_minio_bucket():
    delete_bucket(force=True)
    flash("🗑️ Bucket deleted with contents.", "success")
    return redirect(url_for('admin.system_links'))


@admin_bp.route('/errors')
@admin_only
@login_required
@log_exceptions()
def view_errors():
    from models.models_definitions import ErrorLog
    logs = ErrorLog.query.order_by(ErrorLog.timestamp.desc()).limit(50).all()
    return render_template("admin/error_logs.html", logs=logs)
