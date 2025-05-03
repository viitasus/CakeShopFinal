from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from database.models import db, Product, Category, CartItem, Order, Address, Discount
from datetime import datetime

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
    search_term = request.args.get('search')
    
    # Get all categories
    categories = Category.query.all()
    
    return render_template('menu.html', categories=categories, active_category=category_slug, search_term=search_term)

@main.route('/product/<product_slug>')
def product(product_slug):
    """Render the product detail page"""
    product = Product.query.filter_by(slug=product_slug).first_or_404()
    
    # Get related products (same category)
    related_products = []
    if product.categories:
        category = product.categories[0]
        related_products = category.products.filter(Product.id != product.id, Product.is_available == True).limit(4).all()
    
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    # Get user's orders with pagination
    pagination = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    orders = pagination.items
    
    return render_template('profile/orders.html', orders=orders, pagination=pagination)

@main.route('/profile/addresses')
@login_required
def profile_addresses():
    """Render the addresses page"""
    # Get user's addresses
    addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc()).all()
    
    return render_template('profile/addresses.html', addresses=addresses)

@main.route('/profile/settings')
@login_required
def profile_settings():
    """Render the settings page"""
    return render_template('profile/settings.html')

@main.route('/order/confirmation/<order_id>')
@login_required
def order_confirmation(order_id):
    """Render the order confirmation page"""
    # Remove "ORD" prefix if present and convert to integer
    if order_id.startswith('ORD'):
        order_id = order_id[3:]
    
    try:
        order_id_int = int(order_id)
    except ValueError:
        flash('Invalid order ID', 'error')
        return redirect(url_for('main.profile_orders'))
    
    # Get order
    order = Order.query.filter_by(id=order_id_int, user_id=current_user.id).first_or_404()
    
    # Format order ID
    formatted_order_id = f"ORD{order.id:08d}"
    
    return render_template('order/confirmation.html', order=order, formatted_order_id=formatted_order_id)

@main.route('/order/<order_id>')
@login_required
def order_details(order_id):
    """Render the order details page"""
    # Remove "ORD" prefix if present and convert to integer
    if order_id.startswith('ORD'):
        order_id = order_id[3:]
    
    try:
        order_id_int = int(order_id)
    except ValueError:
        flash('Invalid order ID', 'error')
        return redirect(url_for('main.profile_orders'))
    
    # Get order
    order = Order.query.filter_by(id=order_id_int, user_id=current_user.id).first_or_404()
    
    # Format order ID
    formatted_order_id = f"ORD{order.id:08d}"
    
    # Get shipping address
    shipping_address = Address.query.get(order.shipping_address_id)
    
    return render_template(
        'order/details.html', 
        order=order, 
        formatted_order_id=formatted_order_id,
        shipping_address=shipping_address
    )

@main.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@main.route('/contact')
def contact():
    """Render the contact page"""
    return render_template('contact.html')

@main.route('/search')
def search():
    """Handle search requests"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
    
    return redirect(url_for('main.menu', search=query))

@main.route('/api/coupon/apply', methods=['POST'])
def apply_coupon():
    """API endpoint to apply a coupon code"""
    data = request.get_json()
    code = data.get('code', '').upper()
    
    # Find discount by code
    discount = Discount.query.filter_by(code=code, is_active=True).first()
    
    if not discount:
        return jsonify({
            'success': False,
            'message': 'Invalid coupon code'
        })
    
    # Check if discount is valid (date range)
    now = datetime.utcnow()
    if discount.start_date > now or (discount.end_date and discount.end_date < now):
        return jsonify({
            'success': False,
            'message': 'This coupon has expired'
        })
    
    # Calculate discount amount
    if current_user.is_authenticated:
        # Get cart total
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_total = sum(float(item.product.price) * item.quantity for item in cart_items)
        
        # Check minimum purchase requirement
        if discount.min_purchase and cart_total < float(discount.min_purchase):
            return jsonify({
                'success': False,
                'message': f'Minimum purchase of ₹{float(discount.min_purchase)} required'
            })
        
        # Calculate discount
        if discount.is_percentage:
            discount_amount = cart_total * (float(discount.amount) / 100)
        else:
            discount_amount = float(discount.amount)
        
        # Ensure discount doesn't exceed cart total
        if discount_amount > cart_total:
            discount_amount = cart_total
        
        # Store discount in session
        session['discount_code'] = code
        session['discount_amount'] = discount_amount
        
        # Return discount info
        return jsonify({
            'success': True,
            'message': f'Coupon applied: {discount.description}',
            'discount': round(discount_amount)
        })
    else:
        return jsonify({
            'success': False,
            'message': 'You must be logged in to apply a coupon'
        })

# Error handlers
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Custom template filters
@main.app_template_filter('thousands_separator')
def thousands_separator(value):
    """Add thousands separator to number"""
    return "{:,}".format(value)