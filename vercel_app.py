# Vercel entry point for Flask application
import os
from app import create_app

# Create the Flask application instance
app = create_app()

# Vercel expects the application to be available in the global scope
# This file serves as the WSGI entry point
if __name__ == "__main__":
    app.run()