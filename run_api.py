#!/usr/bin/env python3
"""
Quick start script for Flask API.
Runs the REST API server.
"""
import sys
import os
 
# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import Flask app
from api.flask_api import app

if __name__ == "__main__":
    # Run Flask development server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
