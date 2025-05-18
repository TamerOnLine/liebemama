from werkzeug.utils import secure_filename
import uuid
from routes.minio_client import get_minio_client, get_minio_bucket

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort, current_app
from models.models_definitions import db, ProductImage, Product
from routes.auth_utils import login_required

product_images_bp = Blueprint('product_images', __name__)

@product_images_bp.route('/products/<int:product_id>/images')
@login_required
def manage_product_images(product_id):
    product = Product.query.get_or_404(product_id)
    role = session.get('role')
    user_id = session.get('user_id')

    if role == 'merchant' and product.merchant_id != user_id:
        current_app.logger.warning(f"🛑 Unauthorized access by merchant {user_id} to product {product_id}")
        abort(403)

    return render_template('shared/manage_images.html', product=product)


@product_images_bp.route('/images/<int:image_id>/set-main', methods=['POST'])
@login_required
def set_main_image(image_id):
    img = ProductImage.query.get_or_404(image_id)
    product = img.product

    role = session.get('role')
    user_id = session.get('user_id')
    if role == 'merchant' and product.merchant_id != user_id:
        abort(403)

    for i in product.images:
        i.is_main = (i.id == image_id)

    db.session.commit()
    flash("✅ تم تعيين الصورة كصورة رئيسية", "success")
    return redirect(request.referrer or url_for('merchant.my_products'))


@product_images_bp.route('/products/<int:product_id>/upload', methods=['POST'])
@login_required
def upload_image(product_id):
    product = Product.query.get_or_404(product_id)

    role = session.get('role')
    user_id = session.get('user_id')
    if role == 'merchant' and product.merchant_id != user_id:
        abort(403)

    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("❌ لا يوجد ملف مرفوع", "error")
        return redirect(request.referrer)

    try:
        filename = secure_filename(image_file.filename)
        folder = f"products/{role}/{user_id}/product_{product.id}"
        object_key = f"{folder}/{uuid.uuid4().hex}_{filename}"

        image_data = image_file.read()
        image_file.stream.seek(0)

        minio_client = get_minio_client()
        bucket_name = get_minio_bucket()

        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        minio_client.put_object(
            bucket_name,
            object_key,
            image_file.stream,
            length=len(image_data),
            part_size=10 * 1024 * 1024,
            content_type=image_file.content_type
        )

        image_url = f"https://files.liebemama.com/{bucket_name}/{object_key}"
        new_image = ProductImage(
            product_id=product.id,
            image_url=image_url,
            is_main=False
        )
        db.session.add(new_image)
        db.session.commit()

        flash("✅ تم رفع الصورة بنجاح", "success")

    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"❌ MinIO Upload Error: {e}")
        flash("⚠️ فشل رفع الصورة. لم يتم حفظها.", "error")

    return redirect(request.referrer or url_for('merchant.my_products'))


@product_images_bp.route('/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id):
    img = ProductImage.query.get_or_404(image_id)
    product = img.product

    role = session.get('role')
    user_id = session.get('user_id')
    if role == 'merchant' and product.merchant_id != user_id:
        abort(403)

    try:
        if img.image_url and 'files.liebemama.com' in img.image_url:
            minio_client = get_minio_client()
            bucket_name = get_minio_bucket()

            prefix = f"https://files.liebemama.com/{bucket_name}/"
            object_key = img.image_url.replace(prefix, "")

            print("🗑️ حذف من MinIO:", object_key)
            minio_client.remove_object(bucket_name, object_key)

        db.session.delete(img)
        db.session.commit()
        flash("🗑️ تم حذف الصورة بنجاح", "success")

    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"❌ Error deleting image: {e}")
        flash("❌ حدث خطأ أثناء حذف الصورة", "error")

    return redirect(request.referrer or url_for('merchant.my_products'))