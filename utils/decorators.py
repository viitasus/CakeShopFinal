# utils/decorators.py
from functools import wraps
from flask import redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user

def admin_required(f):
    """
    Decorator for routes that require admin privileges
    Redirects to home page if user is not an admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_api_required(f):
    """
    Decorator for API routes that require admin privileges
    Returns 403 Forbidden JSON response if user is not an admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def ajax_login_required(f):
    """
    Decorator for AJAX routes that require login
    Returns 401 Unauthorized JSON response if user is not logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def confirmed_account_required(f):
    """
    Decorator for routes that require a confirmed account
    Redirects to confirmation required page if account is not confirmed
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not current_user.is_active:
            flash('Please confirm your account.', 'warning')
            return redirect(url_for('auth.confirm_required'))
        
        return f(*args, **kwargs)
    return decorated_function

def prevent_authenticated(f):
    """
    Decorator for routes that should not be accessed by logged in users
    (e.g., login, registration pages)
    Redirects to home page if user is already logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function