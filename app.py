"""
Flask Application Entry Point
============================

This module imports and exposes the Flask application from the backend.
It serves as the entry point for WSGI servers like Gunicorn.

Usage:
  - Development: python app.py
  - Production: gunicorn -w 4 -b 0.0.0.0:5000 app:app
"""

import sys
import os

# Add project root to Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
