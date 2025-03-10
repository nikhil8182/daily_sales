from app import create_app
from datetime import datetime
import os

# Get environment from ENV variable (default to production for WSGI)
config_name = os.environ.get('FLASK_ENV', 'production')
application = create_app(config_name)

@application.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# For gunicorn
app = application

if __name__ == '__main__':
    application.run()