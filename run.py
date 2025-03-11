from app import create_app
from datetime import datetime
import sys
import os

# Get environment from ENV variable (default to development)
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    port = 5055
    
    # Check for port argument
    if len(sys.argv) > 1 and sys.argv[1] == '--port' and len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port number: {sys.argv[2]}")
            sys.exit(1)
    
    # Get host from environment or default to localhost
    host = os.environ.get('HOST', '127.0.0.1')
    
    # Only enable debug in development
    debug = config_name == 'development'
    
    app.run(host=host, port=port, debug=debug)