from routes.minio_client import get_minio_client, get_minio_bucket
from flask import Blueprint, request, session, current_app, render_template, redirect, url_for, flash
from models.models_definitions import db, Product
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import uuid

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def index():
    try:
        products = Product.query.options(
            joinedload(Product.images)
        ).filter(Product.is_approved == True).all()
        return render_template('index.html', products=products)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Internal error: {e}", 500

@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return render_template('product_detail.html', product=product)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Internal Error: {str(e)}", 500

def get_next_sequence_for_merchant(merchant_id):
    count = Product.query.filter_by(merchant_id=merchant_id).count()
    return count + 1

@products_bp.route('/admin/add_product', methods=['POST'])
def add_product():
    try:
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form.get('description')
        specs = request.form.get('specs')
        image = request.files.get('image')
        merchant_id = 1  # لاحقًا: ربطه بالمستخدم الحقيقي

        if not name or not price:
            flash("❌ Product name and price are required.", "error")
            return redirect(url_for('products.index'))

        sequence = get_next_sequence_for_merchant(merchant_id)
        image_url = None

        if image:
            try:
                filename = secure_filename(image.filename)
                folder = f"products/admin/{merchant_id}/product_temp"
                unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

                image_data = image.read()
                image.stream.seek(0)

                role = session.get("role", "admin")
                minio_client = get_minio_client()
                bucket_name = get_minio_bucket(role)

                minio_client.put_object(
                    bucket_name,
                    unique_filename,
                    image.stream,
                    length=len(image_data),
                    part_size=10 * 1024 * 1024,
                    content_type=image.content_type
                )

                image_url = f"https://files.liebemama.com/{bucket_name}/{unique_filename}"

            except Exception as e:
                current_app.logger.error(f"❌ MinIO upload error: {e}")
                flash("❌ Error uploading image. Please try again later.", "error")
                return redirect(url_for('products.index'))

        product = Product(
            name=name,
            price=price,
            description=description,
            specs=specs,
            image=image_url,
            merchant_id=merchant_id
        )
        product.generate_code(sequence)
        db.session.add(product)
        db.session.commit()

        flash(f"✅ Product added successfully with code: {product.product_code}", "success")
        return redirect(url_for('admin.admin_dashboard'))

    except Exception as e:
        current_app.logger.exception("❌ Error during product creation")
        flash("❌ An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for('products.index'))