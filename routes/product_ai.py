from flask import Blueprint, render_template
from models.models_definitions import Product

product_ai_bp = Blueprint("product_ai", __name__, url_prefix="/products")

@product_ai_bp.route("/<int:product_id>/analyze")
def analyze_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("shared/analyze_product.html", product=product)
