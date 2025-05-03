# services/product_service.py
from database.models import db, Product, Category
from flask import current_app
from slugify import slugify
import os
from werkzeug.utils import secure_filename
import uuid

class ProductService:
    @staticmethod
    def get_all_products(category_slug=None, search_term=None):
        """Get all products with optional filtering"""
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
        
        # Execute and return results
        return query.all()
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get a product by ID"""
        return Product.query.get(product_id)
    
    @staticmethod
    def get_product_by_slug(slug):
        """Get a product by slug"""
        return Product.query.filter_by(slug=slug).first()
    
    @staticmethod
    def get_popular_products(limit=6):
        """Get popular products"""
        # In a real app, this might use sales data or user activity
        # For now, just return available products
        return Product.query.filter_by(is_available=True).limit(limit).all()
    
    @staticmethod
    def get_related_products(product, limit=4):
        """Get related products (same category)"""
        if not product.categories:
            return []
        
        category = product.categories[0]
        return category.products.filter(
            Product.id != product.id, 
            Product.is_available == True
        ).limit(limit).all()
    
    @staticmethod
    def create_product(name, price, description=None, categories=None, image_file=None):
        """Create a new product"""
        try:
            # Generate slug from name
            slug = slugify(name)
            
            # Check if slug exists, if so, make it unique
            if Product.query.filter_by(slug=slug).first():
                slug = f"{slug}-{str(uuid.uuid4())[:8]}"
            
            # Create product
            product = Product(
                name=name,
                slug=slug,
                description=description,
                price=price,
                is_available=True
            )
            
            # Add categories if provided
            if categories:
                for category_id in categories:
                    category = Category.query.get(category_id)
                    if category:
                        product.categories.append(category)
            
            # Handle image upload if provided
            if image_file:
                filename = secure_filename(image_file.filename)
                # Add unique prefix to avoid name collisions
                unique_filename = f"{str(uuid.uuid4())[:8]}_{filename}"
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save file
                image_file.save(image_path)
                
                # Save relative path to database
                product.image_path = f"/static/images/cakes/{unique_filename}"
            
            db.session.add(product)
            db.session.commit()
            
            return True, product.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating product: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def update_product(product_id, data, image_file=None):
        """Update a product"""
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return False, "Product not found"
            
            # Update fields if provided
            if 'name' in data:
                product.name = data['name']
                
                # Update slug if name changed
                if data['name'] != product.name:
                    new_slug = slugify(data['name'])
                    
                    # Check if slug exists, if so, make it unique
                    if Product.query.filter(Product.slug == new_slug, Product.id != product_id).first():
                        new_slug = f"{new_slug}-{str(uuid.uuid4())[:8]}"
                    
                    product.slug = new_slug
            
            if 'description' in data:
                product.description = data['description']
            
            if 'price' in data:
                product.price = data['price']
            
            if 'is_available' in data:
                product.is_available = data['is_available']
            
            # Update categories if provided
            if 'categories' in data:
                # Clear existing categories
                product.categories = []
                
                # Add new categories
                for category_id in data['categories']:
                    category = Category.query.get(category_id)
                    if category:
                        product.categories.append(category)
            
            # Handle image upload if provided
            if image_file:
                # Delete old image if exists
                if product.image_path:
                    old_image_path = os.path.join(current_app.root_path, product.image_path.lstrip('/'))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(image_file.filename)
                # Add unique prefix to avoid name collisions
                unique_filename = f"{str(uuid.uuid4())[:8]}_{filename}"
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save file
                image_file.save(image_path)
                
                # Save relative path to database
                product.image_path = f"/static/images/cakes/{unique_filename}"
            
            db.session.commit()
            
            return True, product.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating product: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def delete_product(product_id):
        """Delete a product"""
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return False, "Product not found"
            
            # Delete image file if exists
            if product.image_path:
                image_path = os.path.join(current_app.root_path, product.image_path.lstrip('/'))
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            db.session.delete(product)
            db.session.commit()
            
            return True, "Product deleted successfully"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting product: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_all_categories():
        """Get all categories"""
        return Category.query.all()
    
    @staticmethod
    def get_category_by_slug(slug):
        """Get a category by slug"""
        return Category.query.filter_by(slug=slug).first()
    
    @staticmethod
    def create_category(name, description=None):
        """Create a new category"""
        try:
            # Generate slug from name
            slug = slugify(name)
            
            # Check if slug exists, if so, make it unique
            if Category.query.filter_by(slug=slug).first():
                slug = f"{slug}-{str(uuid.uuid4())[:8]}"
            
            # Create category
            category = Category(
                name=name,
                slug=slug,
                description=description
            )
            
            db.session.add(category)
            db.session.commit()
            
            return True, category.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating category: {str(e)}")
            return False, str(e)