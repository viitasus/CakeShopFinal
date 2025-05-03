# utils/email_sender.py
from flask import current_app, render_template, url_for
from flask_mail import Message
from threading import Thread
from datetime import datetime

def send_async_email(app, msg):
    """
    Send email asynchronously
    """
    with app.app_context():
        from app import mail
        mail.send(msg)

def send_email(subject, recipients, template_html, template_text=None, **kwargs):
    """
    Send email with rendered templates
    """
    try:
        from app import mail, app
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@happycake.com')
        )
        
        # Render HTML template
        msg.html = render_template(template_html, **kwargs)
        
        # Render text template if provided
        if template_text:
            msg.body = render_template(template_text, **kwargs)
        
        # Send asynchronously
        Thread(target=send_async_email, args=(app, msg)).start()
        
        return True, "Email sent successfully"
    
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False, str(e)

def send_confirmation_email(user):
    """
    Send account confirmation email
    """
    from auth.utils import generate_confirmation_token
    
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    
    return send_email(
        subject="Please Confirm Your Email",
        recipients=[user.email],
        template_html="emails/confirm_email.html",
        template_text="emails/confirm_email.txt",
        user=user,
        confirm_url=confirm_url
    )

def send_password_reset_email(user):
    """
    Send password reset email
    """
    from auth.utils import generate_confirmation_token
    
    token = generate_confirmation_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    return send_email(
        subject="Password Reset Request",
        recipients=[user.email],
        template_html="emails/reset_password.html",
        template_text="emails/reset_password.txt",
        user=user,
        reset_url=reset_url
    )

def send_order_confirmation_email(order):
    """
    Send order confirmation email
    """
    from services.order_service import OrderService
    
    # Format order ID
    formatted_order_id = OrderService.format_order_id(order.id)
    
    return send_email(
        subject=f"Order Confirmation - {formatted_order_id}",
        recipients=[order.user.email],
        template_html="emails/order_confirmation.html",
        template_text="emails/order_confirmation.txt",
        order=order,
        formatted_order_id=formatted_order_id,
        current_date=datetime.utcnow()
    )

def send_order_status_update_email(order):
    """
    Send order status update email
    """
    from services.order_service import OrderService
    
    # Format order ID
    formatted_order_id = OrderService.format_order_id(order.id)
    
    # Get status message
    status_messages = {
        'processing': 'Your order is now being processed. We\'re preparing your cake with love!',
        'shipped': 'Your order has been shipped and is on its way to you!',
        'delivered': 'Your order has been delivered. Enjoy your cake!',
        'cancelled': 'Your order has been cancelled.'
    }
    
    status_message = status_messages.get(order.status, f'Your order status has been updated to: {order.status}')
    
    return send_email(
        subject=f"Order Status Update - {formatted_order_id}",
        recipients=[order.user.email],
        template_html="emails/order_status_update.html",
        template_text="emails/order_status_update.txt",
        order=order,
        formatted_order_id=formatted_order_id,
        status_message=status_message,
        current_date=datetime.utcnow()
    )

def send_contact_form_email(name, email, subject, message):
    """
    Send email from contact form
    """
    try:
        from app import mail, app
        
        msg = Message(
            subject=f"Contact Form: {subject}",
            sender=email,
            reply_to=email,
            recipients=[current_app.config.get('ADMIN_EMAIL', 'info@happycake.com')],
            body=f"""
            Name: {name}
            Email: {email}
            
            Message:
            {message}
            """
        )
        
        # Send asynchronously
        Thread(target=send_async_email, args=(app, msg)).start()
        
        return True, "Your message has been sent successfully!"
    
    except Exception as e:
        current_app.logger.error(f"Error sending contact form email: {str(e)}")
        return False, "An error occurred while sending your message. Please try again later."