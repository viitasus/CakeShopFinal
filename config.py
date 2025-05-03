import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base config class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'happy-cake-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images/cakes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    'postgresql://postgres:1029@localhost:5432/cakeshop'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    'postgresql://postgres:password@localhost/happy_cake_test'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Dictionary of configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}