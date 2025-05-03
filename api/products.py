from flask import Blueprint, jsonify, request
from database.models import db, Product, Category
from flask_login import login_required, current_user

products = Blueprint('products', __name__)

@products.route('/cakes', methods=['GET'])
def get_cakes():
    """Get all cakes or filter by category"""
    category_slug = request.args.get('category')
    search_term = request.args.get('search')
    
    # Start with all available products
    query = Product.query.filter_by(is_available=True)
    
    # Filter by category if provided
    if category_slug and category_slug != 'all':
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = category.products.filter_by(is_available=True)
    
    # Filter by search term if provided
    if search_term:
        search = f"%{search_term}%"
        query = query.filter(Product.name.ilike(search) | Product.description.ilike(search))
    
    # Execute query and format results
    products = query.all()
    result = []
    
    for product in products:
        # Format price with commas and currency symbol
        price_display = f"₹{int(product.price):,}"
        
        # Get category slugs
        category_slugs = [category.slug for category in product.categories]
        
        result.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': price_display,
            'price_value': float(product.price),
            'image': product.image_path or f"/static/images/cakes/{product.slug}.png",
            'description': product.description,
            'categories': category_slugs
        })
    
    return jsonify(result)

@products.route('/cake/<cake_id>', methods=['GET'])
def get_cake(cake_id):
    """Get details for a specific cake"""
    # Try to find by ID first, then by slug
    try:
        cake_id_int = int(cake_id)
        product = Product.query.get(cake_id_int)
    except ValueError:
        product = Product.query.filter_by(slug=cake_id).first()
    
    if not product:
        return jsonify({"error": "Cake not found"}), 404
    
    # Format price with commas and currency symbol
    price_display = f"₹{int(product.price):,}"
    
    # Get category slugs
    category_slugs = [category.slug for category in product.categories]
    
    result = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'price': price_display,
        'price_value': float(product.price),
        'image': product.image_path or f"/static/images/cakes/{product.slug}.png",
        'description': product.description,
        'categories': category_slugs
    }
    
    return jsonify(result)

@products.route('/categories', methods=['GET'])
def get_categories():
    """Get all cake categories"""
    categories = Category.query.all()
    result = []
    
    for category in categories:
        result.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description
        })
    
    return jsonify(result)