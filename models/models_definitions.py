from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Product(db.Model):
    """Database model for products.

    Attributes:
        id (int): Primary key.
        name (str): Name of the product.
        price (float): Price of the product.
        description (str): Product description.
        image (str): URL or path to the product image.
        specs (str): Specifications of the product.
        product_code (str): Unique code identifying the product.
        merchant_id (int): Foreign key to the User (merchant).
        is_approved (bool): Approval status of the product.
        updated_at (datetime): Last update timestamp.
    """

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    specs = db.Column(db.Text)
    product_code = db.Column(db.String(30), unique=True, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)  # Set default approval as False
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        """Return a string representation of the product."""
        return f'<Product {self.name}>'

    def generate_code(self, sequence):
        """Generate a unique product code based on merchant ID and sequence."""
        if self.merchant_id:
            self.product_code = f"USR{self.merchant_id:06d}-PRO{sequence:03d}"


class User(db.Model):
    """Database model for users.

    Attributes:
        id (int): Primary key.
        email (str): User's email address.
        username (str): Unique username.
        password_hash (str): Hashed password.
        role (str): Role of the user (e.g., user, admin).
        products (list): List of products associated with the user.
        created_at (datetime): Account creation timestamp.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default='user')
    products = db.relationship('Product', backref='merchant', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Generate and store a password hash.

        Args:
            password (str): The plaintext password to hash.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the provided password against the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Return a string representation of the user."""
        return f'<User {self.username}>'


class Notification(db.Model):
    """Database model for notifications.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the user.
        role (str): Role of the user to notify (admin, merchant, customer, visitor).
        type (str): Type of notification (info, success, error).
        message (str): Notification message.
        product_id (int): Foreign key to the associated product.
        order_id (int): Optional foreign key to the associated order.
        is_read (bool): Status of whether the notification has been read.
        is_visible (bool): Status of whether the notification is visible.
        created_at (datetime): Timestamp of when the notification was created.
    """

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # admin, merchant, customer, visitor
    type = db.Column(db.String(50), nullable=False, default='info')  # Default type is 'info'
    message = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    order_id = db.Column(db.Integer, nullable=True)
    is_read = db.Column(db.Boolean, default=False)  # Default is unread
    is_visible = db.Column(db.Boolean, default=True)  # Default is visible
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the notification."""
        return f"<Notification {self.id} to {self.role} ({self.type})>"


class ProductImage(db.Model):
    """Database model for multiple images per product.

    Attributes:
        id (int): Primary key.
        product_id (int): Foreign key to the associated product.
        image_url (str): URL of the image.
        is_main (bool): Indicates if this is the main image.
        created_at (datetime): Timestamp of image upload.
    """

    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='images')

    def __repr__(self):
        return f"<ProductImage product_id={self.product_id} is_main={self.is_main}>"


class NutritionalAnalysis(db.Model):
    __tablename__ = 'nutritional_analyses'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    language = db.Column(db.String(10), default='ar')

    analysis_summary = db.Column(db.Text, nullable=False)
    benefits = db.Column(db.Text)
    risks = db.Column(db.Text)
    nutritional_values_json = db.Column(db.Text)  # Can be JSON stringified dict

    ai_prompt = db.Column(db.Text)
    ai_response_raw = db.Column(db.Text)
    source_model = db.Column(db.String(50), default='unknown')
    confidence_score = db.Column(db.Float)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref='nutritional_analyses')



class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"


from datetime import datetime
from models.models_definitions import db

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="success")  # success / error
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AdminLog {self.action} - {self.status}>"
