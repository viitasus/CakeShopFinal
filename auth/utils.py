# auth/utils.py
import re
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_login import login_user, logout_user
from database.models import User

def generate_confirmation_token(email):
    """Generate a secure token for email confirmation"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'email-confirm'))

def confirm_token(token, expiration=3600):
    """Confirm a token is valid and not expired"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'email-confirm'),
            max_age=expiration
        )
        return email
    except (SignatureExpired, BadSignature):
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for at least one lowercase
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def get_password_strength(password):
    """
    Get password strength
    Returns: 'weak', 'medium', or 'strong'
    """
    strength = 0
    
    # Length check
    if len(password) >= 8:
        strength += 1
    if len(password) >= 12:
        strength += 1
    
    # Character type check
    if re.search(r'[A-Z]', password):
        strength += 1
    if re.search(r'[a-z]', password):
        strength += 1
    if re.search(r'\d', password):
        strength += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
    
    # Determine strength category
    if strength < 3:
        return 'weak'
    elif strength < 5:
        return 'medium'
    else:
        return 'strong'