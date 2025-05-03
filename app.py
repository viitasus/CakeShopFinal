import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config as app_config
from database.models import db, User

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name='default'):
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Set up login view
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'info'
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from api.products import products as products_blueprint
    app.register_blueprint(products_blueprint, url_prefix='/api')
    
    from api.cart import cart as cart_blueprint
    app.register_blueprint(cart_blueprint, url_prefix='/api')
    
    from api.orders import orders as orders_blueprint
    app.register_blueprint(orders_blueprint, url_prefix='/api')
    
    from api.users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/api')
    
    # Register main routes
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app