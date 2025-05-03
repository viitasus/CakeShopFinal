from flask import Blueprint, jsonify, request
from database.models import db, Order, OrderItem, Product, CartItem, Address, Discount
from flask_login import login_required, current_user
from datetime import datetime

orders = Blueprint('orders', __name__)

@orders.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get all orders for the current user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    orders_query = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc())
    
    # Get total count
    total_orders = orders_query.count()
    
    # Apply pagination
    orders_paginated = orders_query.paginate(page=page, per_page=per_page, error_out=False)
    orders_list = orders_paginated.items
    
    result = []
    
    for order in orders_list:
        # Format date
        formatted_date = order.created_at.strftime('%B %d, %Y')
        
        # Get shipping address
        shipping_address = order.shipping_address
        address_text = f"{shipping_address.address_line1}, {shipping_address.city}, {shipping_address.state} {shipping_address.postal_code}"
        
        # Get order items
        items = []
        for item in order.items:
            product = item.product
            items.append({
                'product_id': product.id,
                'cake_id': product.slug,
                'cake_name': product.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'total': float(item.price) * item.quantity
            })
        
        # Format order ID
        formatted_order_id = f"ORD{order.id:08d}"
        
        result.append({
            'id': order.id,
            'order_id': formatted_order_id,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'order_date': formatted_date,
            'shipping_address': address_text,
            'delivery_date': order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else None,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status,
            'items': items
        })
    
    return jsonify({
        'success': True,
        'orders': result,
        'total': total_orders,
        'page': page,
        'per_page': per_page,
        'has_more': page * per_page < total_orders
    })

@orders.route('/orders/<order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Get details for a specific order"""
    # Remove "ORD" prefix if present and convert to integer
    if order_id.startswith('ORD'):
        order_id = order_id[3:]
    
    try:
        order_id_int = int(order_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid order ID'}), 400
    
    order = Order.query.filter_by(id=order_id_int, user_id=current_user.id).first()
    
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    # Format date
    formatted_date = order.created_at.strftime('%B %d, %Y')
    
    # Get shipping address
    shipping_address = order.shipping_address
    address_text = f"{shipping_address.address_line1}, {shipping_address.city}, {shipping_address.state} {shipping_address.postal_code}"
    
    # Get order items
    items = []
    for item in order.items:
        product = item.product
        items.append({
            'product_id': product.id,
            'cake_id': product.slug,
            'cake_name': product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'total': float(item.price) * item.quantity
        })
@orders.route('/orders/create', methods=['POST'])
@login_required
def create_order():
    """Create a new order from the user's cart"""
    data = request.get_json()
    
    # Get shipping address
    shipping_address_id = data.get('shipping_address_id')
    address = Address.query.filter_by(id=shipping_address_id, user_id=current_user.id).first()
    
    if not address:
        return jsonify({'success': False, 'message': 'Invalid shipping address'}), 400
    
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'Your cart is empty'}), 400
    
    # Calculate total amount
    total_amount = 0
    for item in cart_items:
        total_amount += float(item.product.price) * item.quantity
    
    # Apply discount if provided
    discount_code = data.get('discount_code')
    discount_amount = 0
    discount = None
    
    if discount_code:
        discount = Discount.query.filter_by(code=discount_code, is_active=True).first()
        
        if discount:
            now = datetime.utcnow()
            
            # Check if discount is valid
            if (discount.start_date <= now and 
                (discount.end_date is None or discount.end_date >= now)):
                
                # Check minimum purchase requirement
                if discount.min_purchase is None or total_amount >= float(discount.min_purchase):
                    if discount.is_percentage:
                        discount_amount = total_amount * (float(discount.amount) / 100)
                    else:
                        discount_amount = float(discount.amount)
                    
                    # Ensure discount doesn't exceed order total
                    if discount_amount > total_amount:
                        discount_amount = total_amount
    
    # Apply discount
    total_amount -= discount_amount
    
    # Get delivery date
    delivery_date_str = data.get('delivery_date')
    delivery_date = None
    
    if delivery_date_str:
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid delivery date format'}), 400
    
    # Get payment method
    payment_method = data.get('payment_method', 'Cash on delivery')
    
    # Create order
    order = Order(
        user_id=current_user.id,
        shipping_address_id=shipping_address_id,
        total_amount=total_amount,
        delivery_date=delivery_date,
        payment_method=payment_method,
        status='pending',
        payment_status='pending'
    )
    
    # Add discount if applied
    if discount and discount_amount > 0:
        order.discounts.append(discount)
    
    db.session.add(order)
    db.session.flush()  # Get order ID without committing
    
    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)
    
    # Clear cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    
    db.session.commit()
    
    # Format order ID
    formatted_order_id = f"ORD{order.id:08d}"
    
    return jsonify({
        'success': True,
        'message': 'Order placed successfully',
        'order_id': formatted_order_id
    })

@orders.route('/orders/cancel/<order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    # Remove "ORD" prefix if present and convert to integer
    if order_id.startswith('ORD'):
        order_id = order_id[3:]
    
    try:
        order_id_int = int(order_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid order ID'}), 400
    
    order = Order.query.filter_by(id=order_id_int, user_id=current_user.id).first()
    
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    # Check if order can be cancelled
    if order.status not in ['pending', 'processing']:
        return jsonify({'success': False, 'message': 'Order cannot be cancelled'}), 400
    
    # Update order status
    order.status = 'cancelled'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Order cancelled successfully'
    })