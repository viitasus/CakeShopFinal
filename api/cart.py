from flask import Blueprint, jsonify, request
from database.models import db, CartItem, Product
from flask_login import login_required, current_user

cart = Blueprint('cart', __name__)

@cart.route('/cart', methods=['GET'])
@login_required
def get_cart():
    """Get the current user's cart"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    result = []
    cart_total = 0
    
    for item in cart_items:
        product = item.product
        item_total = float(product.price) * item.quantity
        cart_total += item_total
        
        result.append({
            'id': item.id,
            'product_id': product.id,
            'cake_id': product.slug,
            'cake_name': product.name,
            'price': float(product.price),
            'quantity': item.quantity,
            'total': item_total,
            'image': product.image_path or f"/static/images/cakes/{product.slug}.png"
        })
    
    return jsonify({
        'success': True,
        'cart_items': result,
        'cart_total': cart_total
    })

@cart.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add an item to the cart"""
    data = request.get_json()
    
    cake_id = data.get('cake_id')
    quantity = int(data.get('quantity', 1))
    
    # Validate quantity
    if quantity < 1:
        quantity = 1
    if quantity > 10:
        quantity = 10
    
    # Get product by ID or slug
    try:
        product_id = int(cake_id)
        product = Product.query.get(product_id)
    except ValueError:
        product = Product.query.filter_by(slug=cake_id).first()
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    # Check if product is already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity += quantity
        if cart_item.quantity > 10:
            cart_item.quantity = 10
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product.id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    # Get updated cart count
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'success': True,
        'message': f"{product.name} added to cart",
        'cart_count': cart_count
    })

@cart.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    """Update cart item quantity"""
    data = request.get_json()
    
    cart_item_id = data.get('cart_item_id')
    quantity = int(data.get('quantity', 1))
    
    # Validate quantity
    if quantity < 1:
        return remove_from_cart()
    if quantity > 10:
        quantity = 10
    
    # Get cart item
    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404
    
    # Update quantity
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cart updated successfully'
    })

@cart.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    """Remove an item from the cart"""
    data = request.get_json()
    
    cart_item_id = data.get('cart_item_id')
    
    # Get cart item
    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404
    
    # Remove cart item
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Item removed from cart'
    })

@cart.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear the entire cart"""
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cart cleared successfully'
    })

@cart.route('/cart/count', methods=['GET'])
@login_required
def get_cart_count():
    """Get the number of items in the cart"""
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'success': True,
        'cart_count': cart_count
    })