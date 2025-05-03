from flask import Blueprint, jsonify, request
from database.models import db, User, Address
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

users = Blueprint('users', __name__)

@users.route('/user/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile information"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone
        }
    })

@users.route('/user/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    data = request.get_json()
    
    # Get fields to update
    name = data.get('name')
    phone = data.get('phone')
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # Update profile
    if name:
        current_user.name = name
    
    if phone:
        current_user.phone = phone
    
    # Update password if provided
    if current_password and new_password:
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone
        }
    })

@users.route('/user/addresses', methods=['GET'])
@login_required
def get_addresses():
    """Get all addresses for the current user"""
    addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc()).all()
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
    
    return jsonify({
        'success': True,
        'addresses': result
    })

@users.route('/user/addresses/add', methods=['POST'])
@login_required
def add_address():
    """Add a new address for the current user"""
    data = request.get_json()
    
    # Get address fields
    label = data.get('label')
    address_line1 = data.get('address_line1')
    address_line2 = data.get('address_line2')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    phone = data.get('phone')
    is_default = data.get('is_default', False)
    
    # Validate required fields
    if not all([label, address_line1, city, state, postal_code]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # If setting as default, reset other addresses
    if is_default:
        Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
    
    # Create new address
    address = Address(
        user_id=current_user.id,
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
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Address added successfully',
        'address_id': address.id
    })

@users.route('/user/addresses/<int:address_id>', methods=['GET'])
@login_required
def get_address(address_id):
    """Get a specific address"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    
    if not address:
        return jsonify({'success': False, 'message': 'Address not found'}), 404
    
    return jsonify({
        'success': True,
        'address': {
            'id': address.id,
            'label': address.label,
            'address_line1': address.address_line1,
            'address_line2': address.address_line2,
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'phone': address.phone,
            'is_default': address.is_default
        }
    })

@users.route('/user/addresses/<int:address_id>', methods=['POST'])
@login_required
def update_address(address_id):
    """Update an address"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    
    if not address:
        return jsonify({'success': False, 'message': 'Address not found'}), 404
    
    data = request.get_json()
    
    # Get fields to update
    label = data.get('label')
    address_line1 = data.get('address_line1')
    address_line2 = data.get('address_line2')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    phone = data.get('phone')
    is_default = data.get('is_default')
    
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
    
    if is_default is not None:
        if is_default and not address.is_default:
            # Reset other default addresses
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        
        address.is_default = is_default
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Address updated successfully'
    })

@users.route('/user/addresses/<int:address_id>/delete', methods=['POST'])
@login_required
def delete_address(address_id):
    """Delete an address"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    
    if not address:
        return jsonify({'success': False, 'message': 'Address not found'}), 404
    
    # Check if this is the only address
    address_count = Address.query.filter_by(user_id=current_user.id).count()
    
    if address_count == 1:
        return jsonify({'success': False, 'message': 'Cannot delete the only address'}), 400
    
    # If deleting default address, set another address as default
    if address.is_default and address_count > 1:
        new_default = Address.query.filter(Address.user_id == current_user.id, Address.id != address_id).first()
        new_default.is_default = True
    
    db.session.delete(address)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Address deleted successfully'
    })