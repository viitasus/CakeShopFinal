# utils/__init__.py
from .decorators import admin_required, admin_api_required, ajax_login_required, confirmed_account_required, prevent_authenticated
from .image_handler import allowed_file, save_cake_image, optimize_image, delete_image, generate_thumbnail
from .validators import validate_email, validate_password, validate_phone, validate_postal_code, validate_delivery_date, validate_coupon_code, validate_credit_card, validate_card_expiry, validate_cvv, validate_upi_id
from .email_sender import send_email, send_confirmation_email, send_password_reset_email, send_order_confirmation_email, send_order_status_update_email, send_contact_form_email

# Export all utility functions
__all__ = [
    'admin_required', 'admin_api_required', 'ajax_login_required', 'confirmed_account_required', 'prevent_authenticated',
    'allowed_file', 'save_cake_image', 'optimize_image', 'delete_image', 'generate_thumbnail',
    'validate_email', 'validate_password', 'validate_phone', 'validate_postal_code', 'validate_delivery_date',
    'validate_coupon_code', 'validate_credit_card', 'validate_card_expiry', 'validate_cvv', 'validate_upi_id',
    'send_email', 'send_confirmation_email', 'send_password_reset_email',
    'send_order_confirmation_email', 'send_order_status_update_email', 'send_contact_form_email'
]