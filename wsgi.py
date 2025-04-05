"""
WSGI configuration for Flask app.

It exposes the WSGI callable as a module-level variable named ``app``.
"""

from app import app

# This is for Gunicorn
application = app