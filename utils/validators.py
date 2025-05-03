# utils/image_handler.py
import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image

def allowed_file(filename):
    """
    Check if file has an allowed extension
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_cake_image(image_file, cake_slug=None):
    """
    Save a cake image with proper formatting and return the file path
    """
    try:
        if not image_file or not allowed_file(image_file.filename):
            return None
        
        # Generate a unique filename
        filename = secure_filename(image_file.filename)
        unique_name = f"{str(uuid.uuid4())[:8]}_{cake_slug or 'cake'}_{filename}"
        
        # Ensure upload folder exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Full path for file
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        
        # Save the original file
        image_file.save(full_path)
        
        # Optimize the image if it's a JPEG or PNG
        lower_ext = filename.rsplit('.', 1)[1].lower()
        if lower_ext in ['jpg', 'jpeg', 'png']:
            optimize_image(full_path, lower_ext)
        
        # Return relative path for storage in database
        return f"/static/images/cakes/{unique_name}"
    
    except Exception as e:
        current_app.logger.error(f"Error saving cake image: {str(e)}")
        return None

def optimize_image(image_path, extension, max_size=(800, 800)):
    """
    Optimize image size and quality
    """
    try:
        image = Image.open(image_path)
        
        # Resize if larger than max_size
        if image.width > max_size[0] or image.height > max_size[1]:
            image.thumbnail(max_size, Image.LANCZOS)
        
        # Save with optimized settings
        if extension in ['jpg', 'jpeg']:
            image.save(image_path, 'JPEG', optimize=True, quality=85)
        elif extension == 'png':
            image.save(image_path, 'PNG', optimize=True)
        
        return True
    
    except Exception as e:
        current_app.logger.error(f"Error optimizing image: {str(e)}")
        return False

def delete_image(image_path):
    """
    Delete an image file if it exists
    """
    try:
        if not image_path:
            return False
        
        # Get absolute path
        abs_path = os.path.join(current_app.root_path, image_path.lstrip('/'))
        
        # Check if file exists
        if os.path.exists(abs_path):
            os.remove(abs_path)
            return True
        
        return False
    
    except Exception as e:
        current_app.logger.error(f"Error deleting image: {str(e)}")
        return False

def generate_thumbnail(image_path, size=(200, 200)):
    """
    Generate a thumbnail for an image and return the path
    """
    try:
        if not image_path:
            return None
        
        # Get absolute path
        abs_path = os.path.join(current_app.root_path, image_path.lstrip('/'))
        
        # Check if file exists
        if not os.path.exists(abs_path):
            return None
        
        # Generate thumbnail path
        filename = os.path.basename(abs_path)
        thumbnail_name = f"thumb_{filename}"
        thumbnail_path = os.path.join(os.path.dirname(abs_path), thumbnail_name)
        
        # Create the thumbnail
        image = Image.open(abs_path)
        image.thumbnail(size, Image.LANCZOS)
        
        # Save the thumbnail
        image.save(thumbnail_path)
        
        # Return relative path for storage in database
        return f"{os.path.dirname(image_path)}/{thumbnail_name}"
    
    except Exception as e:
        current_app.logger.error(f"Error generating thumbnail: {str(e)}")
        return None