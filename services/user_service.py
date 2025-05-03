# services/user_service.py
from database.models import db, User, Address
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from auth.utils import validate_email, validate_password, send_confirmation_email, track_login_attempt

class UserService:
    @staticmethod
    def register_user(email, password, name, phone=None):
        """Register a new user"""
        try:
            # Validate email format
            if not validate_email(email):
                return False, "Invalid email format"
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return False, "Email already registered"
            
            # Validate password strength
            if not validate_password(password):
                return False, "Password does not meet requirements"
            
            # Create new user
            hashed_password = generate_password_hash(password)
            user = User(
                email=email,
                password_hash=hashed_password,
                name=name,
                phone=phone
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Send confirmation email
            try:
                send_confirmation_email(user)
            except Exception as e:
                current_app.logger.error(f"Error sending confirmation email: {str(e)}")
            
            return True, user.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error registering user: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def authenticate_user(email, password, remember=False):
        """Authenticate a user by email and password"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return False, "Email not found"
            
            if not user.is_active:
                return False, "Account is inactive"
            
            if not check_password_hash(user.password_hash, password):
                # Track failed login attempt
                track_login_attempt(user, success=False)
                return False, "Incorrect password"
            
            # Login user
            login_user(user, remember=remember)
            
            # Track successful login
            track_login_attempt(user, success=True)
            
            return True, user
        except Exception as e:
            current_app.logger.error(f"Error authenticating user: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def logout_user():
        """Logout the current user"""
        try:
            logout_user()
            return True, "Logged out successfully"
        except Exception as e:
            current_app.logger.error(f"Error logging out user: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get a user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get a user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def update_user_profile(user_id, name=None, phone=None, current_password=None, new_password=None):
        """Update user profile information"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return False, "User not found"
            
            # Update password if provided
            if current_password and new_password:
                if not check_password_hash(user.password_hash, current_password):
                    return False, "Current password is incorrect"
                
                # Validate new password
                if not validate_password(new_password):
                    return False, "New password does not meet requirements"
                
                user.password_hash = generate_password_hash(new_password)
            
            # Update name if provided
            if name:
                user.name = name
            
            # Update phone if provided
            if phone is not None:  # Allow empty string
                user.phone = phone
            
            db.session.commit()
            
            return True, "Profile updated successfully"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user profile: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_user_addresses(user_id):
        """Get all addresses for a user"""
        try:
            addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc()).all()
            
            result = []
            for address in addresses:
                result.append({
                    'id': address.id,
                    'label': address.label,
                    'address_line1': address.address_line1,
                    'address_line2': address.address_line2,
                    'city': address.city,
                    'state': address.state,
                    'postal_code': address.postal_code,
                    'phone': address.phone,
                    'is_default': address.is_default
                })
            
            return True, result
        except Exception as e:
            current_app.logger.error(f"Error getting user addresses: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def add_user_address(user_id, label, address_line1, city, state, postal_code, address_line2=None, phone=None, is_default=False):
        """Add a new address for a user"""
        try:
            # If setting as default, reset other addresses
            if is_default:
                Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
            
            # Create new address
            address = Address(
                user_id=user_id,
                label=label,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code,
                phone=phone,
                is_default=is_default
            )
            
            db.session.add(address)
            
            # If this is the first address, make it default
            address_count = Address.query.filter_by(user_id=user_id).count()
            if address_count == 0:
                address.is_default = True
            
            db.session.commit()
            
            return True, address.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding user address: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def update_user_address(address_id, user_id, label=None, address_line1=None, address_line2=None, city=None, state=None, postal_code=None, phone=None, is_default=None):
        """Update an existing address"""
        try:
            address = Address.query.filter_by(id=address_id, user_id=user_id).first()
            
            if not address:
                return False, "Address not found"
            
            # Update fields if provided
            if label:
                address.label = label
            
            if address_line1:
                address.address_line1 = address_line1
            
            if address_line2 is not None:  # Allow empty string
                address.address_line2 = address_line2
            
            if city:
                address.city = city
            
            if state:
                address.state = state
            
            if postal_code:
                address.postal_code = postal_code
            
            if phone is not None:  # Allow empty string
                address.phone = phone
            
            # Update default status if provided
            if is_default is not None:
                if is_default and not address.is_default:
                    # Reset other default addresses
                    Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
                
                address.is_default = is_default
            
            db.session.commit()
            
            return True, "Address updated successfully"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user address: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def delete_user_address(address_id, user_id):
        """Delete an address"""
        try:
            address = Address.query.filter_by(id=address_id, user_id=user_id).first()
            
            if not address:
                return False, "Address not found"
            
            # Check if this is the only address
            address_count = Address.query.filter_by(user_id=user_id).count()
            
            if address_count == 1:
                return False, "Cannot delete the only address"
            
            # If deleting default address, set another address as default
            if address.is_default:
                # Find another address to make default
                new_default = Address.query.filter(Address.user_id == user_id, Address.id != address_id).first()
                if new_default:
                    new_default.is_default = True
            
            # Delete the address
            db.session.delete(address)
            db.session.commit()
            
            return True, "Address deleted successfully"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user address: {str(e)}")
            return False, str(e)