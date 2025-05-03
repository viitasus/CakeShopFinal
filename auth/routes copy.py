from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from database.models import Product, Category, CartItem

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Render the homepage"""
    # Get popular products
    popular_products = Product.query.filter_by(is_available=True).limit(6).all()
    
    return render_template('index.html', products=popular_products)

@main.route('/menu')
def menu():
    """Render the menu page"""
    category_slug = request.args.get('category')
    
    # Get all categories
    categories = Category.query.all()
    
    return render_template('menu.html', categories=categories, active_category=category_slug)

@main.route('/product/<product_slug>')
def product(product_slug):
    """Render the product detail page"""
    product = Product.query.filter_by(slug=product_slug).first_or_404()
    
    # Get related products (same category)
    related_products = []
    if product.categories:
        category = product.categories[0]
        related_products = category.products.filter(Product.id != product.id).limit(4).all()
    
    return render_template('product.html', product=product, related_products=related_products)

@main.route('/cart')
def cart():
    """Render the cart page"""
    return render_template('cart.html')

@main.route('/checkout')
@login_required
def checkout():
    """Render the checkout page"""
    # Check if cart is empty
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.cart'))
    
    return render_template('checkout.html')

@main.route('/profile')
@login_required
def profile():
    """Render the profile page"""
    return render_template('profile/dashboard.html')

@main.route('/profile/orders')
@login_required
def profile_orders():
    """Render the orders page"""
    return render_template('profile/orders.html')

@main.route('/profile/addresses')
@login_required
def profile_addresses():
    """Render the addresses page"""
    return render_template('profile/addresses.html')

@main.route('/profile/settings')
@login_required
def profile_settings():
    """Render the settings page"""
    return render_template('profile/settings.html')

@main.route('/order/confirmation/<order_id>')
@login_required
def order_confirmation(order_id):
    """Render the order confirmation page"""
    return render_template('order/confirmation.html', order_id=order_id)

@main.route('/order/<order_id>')
@login_required
def order_details(order_id):
    """Render the order details page"""
    return render_template('order/details.html', order_id=order_id)

@main.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@main.route('/contact')
def contact():
    """Render the contact page"""
    return render_template('contact.html')

# Error handlers
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500