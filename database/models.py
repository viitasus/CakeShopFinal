from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for products and categories (many-to-many)
product_categories = db.Table('product_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    """User model for storing user related data"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    addresses = db.relationship('Address', backref='user', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy=True, cascade="all, delete-orphan")
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, email, password, name, phone=None):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.phone = phone

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Address(db.Model):
    """Address model for storing user addresses"""
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Address {self.label} for User {self.user_id}>'

class Category(db.Model):
    """Category model for cake categories"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    products = db.relationship('Product', secondary=product_categories, 
                               backref=db.backref('categories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Product model for storing cake products"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class CartItem(db.Model):
    """CartItem model for storing items in a user's cart"""
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CartItem {self.product_id} for User {self.user_id}>'

class Order(db.Model):
    """Order model for storing user orders"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(20), default='pending')
    
    # Relationships
    shipping_address = db.relationship('Address')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    discounts = db.relationship('Discount', secondary='order_discounts')
    
    def __repr__(self):
        return f'<Order {self.id} for User {self.user_id}>'

class OrderItem(db.Model):
    """OrderItem model for storing items in an order"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of order
    
    def __repr__(self):
        return f'<OrderItem {self.product_id} in Order {self.order_id}>'

class Discount(db.Model):
    """Discount model for storing discount codes"""
    __tablename__ = 'discounts'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_percentage = db.Column(db.Boolean, default=False)
    min_purchase = db.Column(db.Numeric(10, 2), nullable=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Discount {self.code}>'

# Association table for orders and discounts
order_discounts = db.Table('order_discounts',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('discount_id', db.Integer, db.ForeignKey('discounts.id'), primary_key=True)
)