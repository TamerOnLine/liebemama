import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, current_app, session, flash
)
from werkzeug.utils import secure_filename
import uuid
from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url


# Local imports
from models.models_definitions import Product, db
from routes.auth_utils import login_required, admin_only
from logic.notification_service import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import validate_form
from routes.minio_admin_tools import create_bucket_if_not_exists, delete_bucket


admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/')
@admin_only
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/products')
@admin_only
@login_required
def admin_products():
    try:
        products = Product.query.all()
        return render_template('admin/admin_products.html', products=products)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<pre>{traceback.format_exc()}</pre>", 500


@admin_bp.route('/add', methods=['GET', 'POST'])
@admin_only
@login_required
def admin_add_product():
    if request.method == 'POST':
        data = request.form.to_dict()
        from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
        from models.models_definitions import ProductImage
        from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url

        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])
        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template('admin/add_product.html', errors=result, tinymce_api_key=os.getenv('TINYMCE_API_KEY')), 400

        try:
            sequence = Product.query.count() + 1
            product = Product(
                name=result['name'],
                price=result['price'],
                description=result.get('description'),
                specs=result.get('specs'),
                merchant_id=session.get("user_id")
            )
            product.generate_code(sequence)
            db.session.add(product)
            db.session.flush()

            # تحميل الصور
            files = request.files.getlist('images')
            for index, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    folder = f"products/admin/{session.get('user_id')}/product_{product.id}"
                    unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

                    image_data = file.read()
                    file.stream.seek(0)

                    # ⬇️ تحميل إعدادات MinIO ديناميكيًا
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

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("❌ Error adding product")
            return "An unexpected error occurred. Please try again later.", 500

    return render_template('admin/add_product.html', tinymce_api_key=os.getenv('TINYMCE_API_KEY'))



@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_only
@login_required
def edit_product(product_id):
    from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
    from models.models_definitions import ProductImage
    from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        data = request.form.to_dict()
        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])
        result['description'] = sanitize_rich_text(result.get('description'))
        result['specs'] = sanitize_rich_text(result.get('specs'))

        if not is_valid:
            return render_template('admin/edit_product.html', product=product, errors=result, user_role='admin')

        product.name = result['name']
        product.price = result['price']
        product.description = result.get('description')
        product.specs = result.get('specs')
        product.is_approved = False

        main_image_id = request.form.get('main_image_id')
        if main_image_id:
            for img in product.images:
                img.is_main = (str(img.id) == main_image_id)

        new_images = request.files.getlist('images')
        for file in new_images:
            if file and file.filename:
                try:
                    filename = secure_filename(file.filename)
                    folder = f"products/admin/{session.get('user_id')}/product_{product.id}"
                    unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

                    image_data = file.read()
                    file.stream.seek(0)

                    # ✅ تحميل الإعدادات الديناميكية
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
                    new_img = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_main=False
                    )
                    db.session.add(new_img)
                except Exception as e:
                    current_app.logger.error(f"MinIO upload error: {e}")
                    return "Error uploading image. Please try again later.", 500

        db.session.commit()
        return redirect(url_for('admin.admin_products'))

    return render_template('admin/edit_product.html', product=product, tinymce_api_key=os.getenv('TINYMCE_API_KEY'), user_role='admin')



@admin_bp.route('/delete-image/<int:image_id>', methods=['POST'])
@admin_only
@login_required
def delete_product_image(image_id):
    from models.models_definitions import ProductImage
    image = ProductImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash("✅ Image deleted successfully.", "info")
    return redirect(request.referrer or url_for('admin.admin_products'))


@admin_bp.route('/system-links')
@admin_only
@login_required
def system_links():
    return render_template('admin/system_links.html')


@admin_bp.route('/approve/<int:product_id>', methods=['POST'])
@admin_only
@login_required
def approve_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_approved = True
    db.session.commit()

    advance_notification(
        product_id=product.id,
        from_role='admin',
        from_type='product_edited',
        to_user_id=product.merchant_id,
        to_role='merchant',
        to_type='product_approved',
        message=f"✅ Your product '{product.name}' has been approved."
    )

    return redirect(url_for('admin.admin_products'))


@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@admin_only
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("✅ Product deleted successfully.", "info")
    return redirect(url_for('admin.admin_products'))



@admin_bp.route('/minio/create-bucket', methods=['POST'])
@admin_only
@login_required
def create_minio_bucket():
    create_bucket_if_not_exists()
    flash("✅ تم التحقق من وجود الـ Bucket أو إنشاؤه بنجاح", "success")
    return redirect(url_for('admin.system_links'))


@admin_bp.route('/minio/delete-bucket', methods=['POST'])
@admin_only
@login_required
def delete_minio_bucket():
    delete_bucket(force=True)
    flash("🗑️ تم حذف الـ Bucket وجميع ملفاته", "warning")
    return redirect(url_for('admin.system_links'))


@admin_bp.route('/minio/logs')
@admin_only
@login_required
def minio_logs():
    from models.models_definitions import AdminLog
    logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).all()
    return render_template('admin/minio_logs.html', logs=logs)

