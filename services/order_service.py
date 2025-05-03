# services/order_service.py
from database.models import db, Order, OrderItem, Product, CartItem, Address, Discount
from flask_login import current_user
from flask import current_app, session
from datetime import datetime, timedelta
import uuid

class OrderService:
    @staticmethod
    def get_user_orders(user_id, page=1, per_page=5):
        """Get all orders for a user with pagination"""
        return Order.query.filter_by(user_id=user_id).order_by(
            Order.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_order_by_id(order_id, user_id=None):
        """Get an order by ID, optionally filtering by user"""
        query = Order.query.filter_by(id=order_id)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.first()
    
    @staticmethod
    def format_order_id(order_id):
        """Format an order ID with leading zeros and prefix"""
        return f"ORD{order_id:08d}"
    
    @staticmethod
    def parse_order_id(formatted_id):
        """Parse a formatted order ID to get the numeric ID"""
        if formatted_id.startswith('ORD'):
            try:
                return int(formatted_id[3:])
            except ValueError:
                return None
        return None
    
    @staticmethod
    def create_order(user_id, shipping_address_id, delivery_date=None, 
                     payment_method="Cash on delivery", special_instructions=None, 
                     discount_code=None):
        """Create a new order from the user's cart"""
        try:
            # Validate shipping address
            address = Address.query.filter_by(id=shipping_address_id, user_id=user_id).first()
            if not address:
                return False, "Invalid shipping address", None
            
            # Get cart items
            cart_items = CartItem.query.filter_by(user_id=user_id).all()
            if not cart_items:
                return False, "Your cart is empty", None
            
            # Calculate total amount
            subtotal = sum(float(item.product.price) * item.quantity for item in cart_items)
            
            # Apply discount if provided
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
                        if discount.min_purchase is None or subtotal >= float(discount.min_purchase):
                            if discount.is_percentage:
                                discount_amount = subtotal * (float(discount.amount) / 100)
                            else:
                                discount_amount = float(discount.amount)
                            
                            # Ensure discount doesn't exceed order total
                            if discount_amount > subtotal:
                                discount_amount = subtotal
            
            # Calculate final total
            total_amount = subtotal - discount_amount
            
            # Add delivery fee if applicable (e.g., if total is below free shipping threshold)
            delivery_fee = 50  # Example: ₹50 delivery fee
            if subtotal < 2000:  # Example: Free delivery on orders over ₹2,000
                total_amount += delivery_fee
            
            # Parse delivery date
            parsed_delivery_date = None
            if delivery_date:
                try:
                    if isinstance(delivery_date, str):
                        parsed_delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                    else:
                        parsed_delivery_date = delivery_date
                except ValueError:
                    return False, "Invalid delivery date format", None
            
            # Ensure delivery date is at least 1 day in the future
            tomorrow = datetime.utcnow().date() + timedelta(days=1)
            if parsed_delivery_date and parsed_delivery_date < tomorrow:
                return False, "Delivery date must be at least 1 day in the future", None
            
            # Create order
            order = Order(
                user_id=user_id,
                shipping_address_id=shipping_address_id,
                total_amount=total_amount,
                delivery_date=parsed_delivery_date,
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
            
            # Clear session discount
            if 'discount_code' in session:
                session.pop('discount_code')
            if 'discount_amount' in session:
                session.pop('discount_amount')
            
            db.session.commit()
            
            # Format order ID
            formatted_order_id = OrderService.format_order_id(order.id)
            
            # Send order confirmation email
            try:
                OrderService.send_order_confirmation_email(order)
            except Exception as e:
                current_app.logger.error(f"Error sending order confirmation email: {str(e)}")
            
            return True, "Order placed successfully", formatted_order_id
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating order: {str(e)}")
            return False, str(e), None
    
    @staticmethod
    def cancel_order(order_id, user_id):
        """Cancel an order"""
        try:
            order = Order.query.filter_by(id=order_id, user_id=user_id).first()
            
            if not order:
                return False, "Order not found"
            
            # Check if order can be cancelled
            if order.status not in ['pending', 'processing']:
                return False, "Order cannot be cancelled"
            
            # Update order status
            order.status = 'cancelled'
            db.session.commit()
            
            # Send cancellation email
            try:
                OrderService.send_order_cancellation_email(order)
            except Exception as e:
                current_app.logger.error(f"Error sending order cancellation email: {str(e)}")
            
            return True, "Order cancelled successfully"
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error cancelling order: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def update_order_status(order_id, status, user_id=None):
        """Update order status (admin function)"""
        try:
            # Query order
            query = Order.query.filter_by(id=order_id)
            
            # Filter by user if provided (for customer access)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            order = query.first()
            
            if not order:
                return False, "Order not found"
            
            # Validate status
            valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
            if status not in valid_statuses:
                return False, "Invalid status"
            
            # Prevent certain status changes
            if order.status == 'cancelled' and status != 'cancelled':
                return False, "Cannot change status of cancelled order"
            
            if order.status == 'delivered' and status not in ['delivered', 'cancelled']:
                return False, "Cannot change status of delivered order"
            
            # Update status
            order.status = status
            
            # Update payment status if order is delivered
            if status == 'delivered':
                order.payment_status = 'paid'
            
            db.session.commit()
            
            # Send status update email
            try:
                OrderService.send_order_status_update_email(order)
            except Exception as e:
                current_app.logger.error(f"Error sending order status update email: {str(e)}")
            
            return True, "Order status updated successfully"
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating order status: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_order_summary(order_id, user_id=None):
        """Get order summary for display"""
        try:
            # Query order
            query = Order.query.filter_by(id=order_id)
            
            # Filter by user if provided (for customer access)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            order = query.first()
            
            if not order:
                return None
            
            # Get order items
            items = []
            subtotal = 0
            
            for item in order.items:
                product = item.product
                item_total = float(item.price) * item.quantity
                subtotal += item_total
                
                items.append({
                    'product_id': product.id,
                    'cake_id': product.slug,
                    'cake_name': product.name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total': item_total,
                    'image': product.image_path or f"/static/images/cakes/{product.slug}.png"
                })
            
            # Calculate discount
            discount = 0
            if order.discounts:
                discount_obj = order.discounts[0]
                if discount_obj.is_percentage:
                    discount = subtotal * (float(discount_obj.amount) / 100)
                else:
                    discount = float(discount_obj.amount)
            
            # Get delivery fee
            delivery_fee = 50  # Default delivery fee
            if subtotal >= 2000:  # Free delivery threshold
                delivery_fee = 0
            
            # Format order ID
            formatted_order_id = OrderService.format_order_id(order.id)
            
            # Format date
            formatted_date = order.created_at.strftime('%B %d, %Y')
            
            # Get shipping address
            shipping_address = order.shipping_address
            address_text = f"{shipping_address.address_line1}, {shipping_address.city}, {shipping_address.state} {shipping_address.postal_code}"
            
            # Return order summary
            return {
                'id': order.id,
                'order_id': formatted_order_id,
                'total_amount': float(order.total_amount),
                'subtotal': subtotal,
                'discount': discount,
                'delivery_fee': delivery_fee,
                'status': order.status,
                'order_date': formatted_date,
                'shipping_address': address_text,
                'delivery_date': order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else None,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'items': items
            }
        
        except Exception as e:
            current_app.logger.error(f"Error getting order summary: {str(e)}")
            return None
    
    @staticmethod
    def send_order_confirmation_email(order):
        """Send order confirmation email"""
        from app import mail
        from flask_mail import Message
        
        # Format order ID
        formatted_order_id = OrderService.format_order_id(order.id)
        
        # Get user
        user = order.user
        
        # Get order items
        items_html = ""
        for item in order.items:
            product = item.product
            item_html = f"""
            <tr>
                <td>{product.name}</td>
                <td>{item.quantity}</td>
                <td>₹{float(item.price)}</td>
                <td>₹{float(item.price) * item.quantity}</td>
            </tr>
            """
            items_html += item_html
        
        # Get shipping address
        address = order.shipping_address
        address_text = f"{address.address_line1}, {address.address_line2 or ''}, {address.city}, {address.state} {address.postal_code}"
        
        # Create email HTML
        html = f"""
        <h2>Order Confirmation</h2>
        <p>Dear {user.name},</p>
        <p>Thank you for your order. We're baking your happiness!</p>
        
        <h3>Order Details</h3>
        <p><strong>Order Number:</strong> {formatted_order_id}</p>
        <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
        <p><strong>Payment Method:</strong> {order.payment_method}</p>
        <p><strong>Order Status:</strong> {order.status}</p>
        
        <h3>Shipping Address</h3>
        <p>{address_text}</p>
        
        <h3>Delivery Information</h3>
        <p><strong>Estimated Delivery:</strong> {order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else 'Within 24-48 hours'}</p>
        
        <h3>Order Summary</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <th>Item</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
            {items_html}
            <tr>
                <td colspan="3" align="right"><strong>Subtotal:</strong></td>
                <td>₹{sum(float(item.price) * item.quantity for item in order.items)}</td>
            </tr>
            <tr>
                <td colspan="3" align="right"><strong>Delivery Fee:</strong></td>
                <td>₹{50 if sum(float(item.price) * item.quantity for item in order.items) < 2000 else 0}</td>
            </tr>
            <tr>
                <td colspan="3" align="right"><strong>Total:</strong></td>
                <td>₹{float(order.total_amount)}</td>
            </tr>
        </table>
        
        <p>If you have any questions about your order, please contact us at support@happycake.com or call +91 98765 43210.</p>
        
        <p>Thank you for choosing Happy Cake!</p>
        <p>The Happy Cake Team</p>
        """
        
        # Create message
        msg = Message(
            subject=f"Order Confirmation - {formatted_order_id}",
            recipients=[user.email],
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@happycake.com')
        )
        
        # Send email
        mail.send(msg)
    
    @staticmethod
    def send_order_cancellation_email(order):
        """Send order cancellation email"""
        from app import mail
        from flask_mail import Message
        
        # Format order ID
        formatted_order_id = OrderService.format_order_id(order.id)
        
        # Get user
        user = order.user
        
        # Create email HTML
        html = f"""
        <h2>Order Cancellation</h2>
        <p>Dear {user.name},</p>
        <p>Your order has been cancelled as requested.</p>
        
        <h3>Order Details</h3>
        <p><strong>Order Number:</strong> {formatted_order_id}</p>
        <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
        
        <p>If you have any questions, please contact us at support@happycake.com or call +91 98765 43210.</p>
        
        <p>Thank you for choosing Happy Cake!</p>
        <p>The Happy Cake Team</p>
        """
        
        # Create message
        msg = Message(
            subject=f"Order Cancellation - {formatted_order_id}",
            recipients=[user.email],
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@happycake.com')
        )
        
        # Send email
        mail.send(msg)
    
    @staticmethod
    def send_order_status_update_email(order):
        """Send order status update email"""
        from app import mail
        from flask_mail import Message
        
        # Format order ID
        formatted_order_id = OrderService.format_order_id(order.id)
        
        # Get user
        user = order.user
        
        # Get status message
        status_messages = {
            'processing': 'Your order is now being processed. We\'re preparing your cake with love!',
            'shipped': 'Your order has been shipped and is on its way to you!',
            'delivered': 'Your order has been delivered. Enjoy your cake!',
            'cancelled': 'Your order has been cancelled.'
        }
        
        status_message = status_messages.get(order.status, f'Your order status has been updated to: {order.status}')
        
        # Create email HTML
        html = f"""
        <h2>Order Status Update</h2>
        <p>Dear {user.name},</p>
        <p>{status_message}</p>
        
        <h3>Order Details</h3>
        <p><strong>Order Number:</strong> {formatted_order_id}</p>
        <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
        <p><strong>Current Status:</strong> {order.status}</p>
        
        <p>You can view your order details <a href="https://happycake.com/order/{formatted_order_id}">here</a>.</p>
        
        <p>If you have any questions, please contact us at support@happycake.com or call +91 98765 43210.</p>
        
        <p>Thank you for choosing Happy Cake!</p>
        <p>The Happy Cake Team</p>
        """
        
        # Create message
        msg = Message(
            subject=f"Order Status Update - {formatted_order_id}",
            recipients=[user.email],
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@happycake.com')
        )
        
        # Send email
        mail.send(msg)