from flask import Flask
from app.models import db
import os
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    with app.app_context():
        # Create the database and tables if they don't exist
        db.create_all()
        
        # Check if we need to create some initial data
        from app.models import TeamMember
        if TeamMember.query.count() == 0:
            # Add some example data
            sample_managers = [
                TeamMember(name="Manager 1", role="SM", active=True),
                TeamMember(name="Manager 2", role="SM", active=True)
            ]
            db.session.add_all(sample_managers)
            db.session.commit()
    
    from app.routes import main
    app.register_blueprint(main.bp)
    
    # Configure error pages
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app