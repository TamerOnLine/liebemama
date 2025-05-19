import os
import uuid
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, abort, current_app, flash
)
from werkzeug.utils import secure_filename

from models.models_definitions import Product, db, User
from flask_login import login_required, current_user
from logic.notification_service import create_notification, get_user_notifications
from logic.notification_flow import advance_notification
from logic.validation_utils import (
    validate_email, validate_password, sanitize_text,
    validate_price, validate_form, coerce_price, sanitize_rich_text
)
from routes.minio_client import get_minio_client, get_minio_bucket, get_minio_base_url
from logic.decorators import log_exceptions


merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def merchant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'merchant':
            current_app.logger.warning(
                "Unauthorized access attempt by user %s",
                current_user.username if current_user.is_authenticated else 'Anonymous'
            )
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@merchant_bp.route('/dashboard')
@login_required
@merchant_required
@log_exceptions()
def dashboard():
    return render_template('merchant/dashboard.html', username=current_user.username)


@merchant_bp.route('/add', methods=['GET', 'POST'])
@login_required
@merchant_required
@log_exceptions()
def add_product():
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
            merchant_id=current_user.id,
            is_approved=False
        )

        sequence = Product.query.filter_by(merchant_id=current_user.id).count() + 1
        product.generate_code(sequence)

        from models.models_definitions import ProductImage

        db.session.add(product)
        db.session.flush()

        files = request.files.getlist('images')
        for index, file in enumerate(files):
            if file and file.filename:
                filename = secure_filename(file.filename)
                folder = f"products/merchant/{current_user.id}/product_{product.id}"
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
            message=f"New product from merchant {current_user.username} awaiting approval"
        )

        return redirect(url_for('merchant.dashboard'))

    return render_template('merchant/add_product.html')


@merchant_bp.route('/my-products')
@login_required
@merchant_required
@log_exceptions()
def my_products():
    products = Product.query.filter_by(merchant_id=current_user.id).all()
    return render_template('merchant/my_products.html', products=products)


@merchant_bp.route('/profile')
@login_required
@merchant_required
@log_exceptions()
def profile():
    user = User.query.get_or_404(current_user.id)
    return render_template('merchant/profile.html', user=user)


@merchant_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@merchant_required
@log_exceptions()
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.merchant_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        schema = {
            'name': {'type': 'string', 'minlength': 2, 'maxlength': 100, 'required': True},
            'price': {'type': 'float', 'min': 0, 'required': True, 'coerce': coerce_price},
            'description': {'type': 'string', 'required': False},
            'specs': {'type': 'string', 'required': False}
        }

        data = request.form.to_dict()
        is_valid, result = validate_form(data, schema, sanitize_fields=['name'])

        if not is_valid:
            return render_template('merchant/edit_product.html', product=product, errors=result)

        product.name = result['name']
        product.price = result['price']
        product.description = sanitize_rich_text(result.get('description'))
        product.specs = sanitize_rich_text(result.get('specs'))

        db.session.commit()
        flash("✅ Product updated successfully", "success")
        return redirect(url_for('merchant.my_products'))

    return render_template('merchant/edit_product.html', product=product)


@merchant_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@merchant_required
@log_exceptions()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.merchant_id != current_user.id:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash("🗑️ Product deleted successfully", "success")
    return redirect(url_for('merchant.my_products'))


@merchant_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
@merchant_required
@log_exceptions()
def edit_profile():
    user = User.query.get_or_404(current_user.id)

    if request.method == 'POST':
        data = request.form.to_dict()
        schema = {
            'username': {'type': 'string', 'minlength': 3, 'maxlength': 30, 'required': True},
            'email': {
                'type': 'string',
                'regex': r'^[^@]+@[^@]+\.[^@]+$',
                'required': True
            }
        }

        is_valid, result = validate_form(data, schema, sanitize_fields=['username'])

        if not is_valid:
            return render_template('merchant/edit_profile.html', user=user, errors=result)

        user.username = result['username']
        user.email = result['email']
        db.session.commit()
        flash('✅ Profile updated successfully', 'success')
        return redirect(url_for('merchant.profile'))

    return render_template('merchant/edit_profile.html', user=user)
