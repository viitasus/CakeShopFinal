from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from database.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from auth.utils import validate_email, validate_password, get_password_strength

# Create blueprint
auth = Blueprint('auth', __name__)

@auth.route('/auth')
def index():
    return render_template('index.html')  # Make sure 'index.html' exists in your 'templates' folder

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Render the login page and handle login requests"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        # If it's an AJAX request
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '')
            password = data.get('password', '')
            remember = data.get('remember', False)
            
            # Validate input
            if not email or not password:
                return jsonify({'success': False, 'message': 'Please enter email and password'})
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return jsonify({'success': False, 'message': 'Invalid email or password'})
            
            # Log in the user
            login_user(user, remember=remember)
            
            return jsonify({'success': True, 'redirect': url_for('auth.index')})
        
        # If it's a regular form submission
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            # Validate input
            if not email or not password:
                flash('Please enter email and password', 'error')
                return render_template('login.html')
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                flash('Invalid email or password', 'error')
                return render_template('login.html')
            
            # Log in the user
            login_user(user, remember=remember)
            
            return redirect(url_for('auth.index'))
    
    # GET request - render login form
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Render the registration page and handle registration requests"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        # If it's an AJAX request
        if request.is_json:
            data = request.get_json()
            name = data.get('name', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            terms = data.get('terms', False)
            
            # Validate input
            if not name or not email or not password:
                return jsonify({'success': False, 'message': 'Please fill in all required fields'})
            
            if password != confirm_password:
                return jsonify({'success': False, 'message': 'Passwords do not match'})
            
            if not terms:
                return jsonify({'success': False, 'message': 'You must agree to the terms and conditions'})
            
            # Validate email format
            if not validate_email(email):
                return jsonify({'success': False, 'message': 'Invalid email address'})
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return jsonify({'success': False, 'message': 'Email already registered'})
            
            # Validate password strength
            if not validate_password(password):
                return jsonify({
                    'success': False, 
                    'message': 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character'
                })
            
            # Create new user
            new_user = User(email=email, password=password, name=name, phone=phone)
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            login_user(new_user)
            
            return jsonify({'success': True, 'redirect': url_for('auth.index')})
        
        # If it's a regular form submission
        else:
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm-password')
            terms = True if request.form.get('terms') else False
            
            # Validate input
            if not name or not email or not password:
                flash('Please fill in all required fields', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register.html')
            
            if not terms:
                flash('You must agree to the terms and conditions', 'error')
                return render_template('register.html')
            
            # Validate email format
            if not validate_email(email):
                flash('Invalid email address', 'error')
                return render_template('register.html')
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('register.html')
            
            # Validate password strength
            if not validate_password(password):
                flash('Password must be at least 8 characters and include uppercase, lowercase, number, and special character', 'error')
                return render_template('register.html')
            
            # Create new user
            new_user = User(email=email, password=password, name=name, phone=phone)
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            login_user(new_user)
            
            return redirect(url_for('auth.index'))
    
    # GET request - render registration form
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    
    # If it's an AJAX request
    if request.is_json:
        return jsonify({'success': True})
    
    # Regular request
    return redirect(url_for('auth.index'))

@auth.route('/check-email', methods=['POST'])
def check_email():
    """Check if an email is already registered"""
    data = request.get_json()
    email = data.get('email', '')
    
    if not email or not validate_email(email):
        return jsonify({'valid': False, 'message': 'Invalid email address'})
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify({'valid': False, 'message': 'Email already registered'})
    
    return jsonify({'valid': True})

@auth.route('/check-password-strength', methods=['POST'])
def check_password_strength():
    """Check the strength of a password"""
    data = request.get_json()
    password = data.get('password', '')
    
    if not password:
        return jsonify({'strength': 'weak', 'valid': False})
    
    strength = get_password_strength(password)
    valid = validate_password(password)
    
    return jsonify({'strength': strength, 'valid': valid})