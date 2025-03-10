from flask import Flask
import os
from config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Verify Firebase key file exists
    firebase_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fb_key_1.json')
    if not os.path.exists(firebase_key_path):
        logger.error(f"Firebase key file not found at: {firebase_key_path}")
        raise RuntimeError(f"Firebase key file not found at: {firebase_key_path}")
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main.bp)
    
    # Configure error pages
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app