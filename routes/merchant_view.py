import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, abort, current_app, flash
)
from models.models_definitions import Product, db, User
from routes.auth_utils import login_required
from logic.notification_service import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import validate_email, validate_password, sanitize_text, validate_price
from functools import wraps
from logic.validation_utils import validate_form
from werkzeug.utils import secure_filename
import uuid
from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url


merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def merchant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'merchant':
            current_app.logger.warning(f"Unauthorized access attempt by user {session.get('username')}")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@merchant_bp.route('/dashboard')
@login_required
@merchant_required
def dashboard():
    return render_template('merchant/dashboard.html', username=session['username'])


@merchant_bp.route('/add', methods=['GET', 'POST'])
@login_required
@merchant_required
def add_product():
    from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
    from models.models_definitions import ProductImage
    from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url

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
            return render_template('merchant/add_product.html', errors=result), 400

        product = Product(
            name=result['name'],
            price=result['price'],
            description=result.get('description'),
            specs=result.get('specs'),
            merchant_id=session['user_id'],
            is_approved=False
        )
        sequence = Product.query.filter_by(merchant_id=session['user_id']).count() + 1
        product.generate_code(sequence)

        try:
            db.session.add(product)
            db.session.flush()

            files = request.files.getlist('images')
            for index, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    folder = f"products/merchant/{session['user_id']}/product_{product.id}"
                    unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

                    image_data = file.read()
                    file.stream.seek(0)

                    # ✅ تحميل إعدادات MinIO من قاعدة البيانات
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
                    img = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_main=(index == 0)
                    )
                    db.session.add(img)

            db.session.commit()

            advance_notification(
                product_id=product.id,
                from_role=None,
                from_type=None,
                to_user_id=None,
                to_role='admin',
                to_type='product_edited',
                message=f"📝 New product from merchant {session['username']} awaiting approval"
            )

            return redirect(url_for('merchant.dashboard'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ Error saving product: {e}")
            return "Unexpected error", 500

    return render_template('merchant/add_product.html')



@merchant_bp.route('/profile')
@login_required
@merchant_required
def profile():
    user = User.query.get_or_404(session['user_id'])
    return render_template('merchant/profile.html', user=user)


@merchant_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@merchant_required
def edit_profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username'].strip()
        user.email = request.form['email'].strip()
        db.session.commit()
        return redirect(url_for('merchant.profile'))

    return render_template('merchant/edit_profile.html', user=user)


@merchant_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@merchant_required
def edit_product(product_id):
    from logic.validation_utils import validate_form, coerce_price, sanitize_rich_text
    from models.models_definitions import ProductImage
    from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url

    product = Product.query.get_or_404(product_id)
    if product.merchant_id != session['user_id']:
        abort(403)

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
            return render_template('merchant/edit_product.html', product=product, errors=result), 400

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
                    folder = f"products/merchant/{session['user_id']}/product_{product.id}"
                    unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

                    image_data = file.read()
                    file.stream.seek(0)

                    # ✅ تحميل إعدادات MinIO
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
                    img = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_main=False
                    )
                    db.session.add(img)
                except Exception as e:
                    current_app.logger.error(f"Error uploading image: {e}")
                    return "Error uploading image", 500

        db.session.commit()
        return redirect(url_for('merchant.my_products'))

    return render_template('merchant/edit_product.html', product=product)



@merchant_bp.route('/products')
@login_required
@merchant_required
def my_products():
    products = Product.query.filter_by(merchant_id=session['user_id']).all()
    return render_template('merchant/my_products.html', products=products)


@merchant_bp.route('/products/<int:product_id>/edit-image', methods=['GET'])
@login_required
@merchant_required
def edit_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if product.merchant_id != session['user_id']:
        abort(403)
    return render_template('shared/edit_image.html', product=product)


@merchant_bp.route('/products/<int:product_id>/save-image', methods=['POST'])
@login_required
@merchant_required
def save_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if product.merchant_id != session['user_id']:
        abort(403)

    image_data = request.form.get('image_data')
    if not image_data:
        flash("❌ لم يتم استلام الصورة الجديدة", "error")
        return redirect(url_for('merchant.edit_product_image', product_id=product_id))

    # لا يوجد رفع مباشر هنا، يُفترض استخدام واجهة أخرى
    flash("⚠️ هذه الميزة غير مفعلة حالياً.", "warning")
    return redirect(url_for('merchant.edit_product', product_id=product.id))