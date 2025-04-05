import os

# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = 1
reload = True
wsgi_app = "main:app"

# Configure logging
errorlog = "-"  # stderr
accesslog = "-"  # stdout
loglevel = "info"

# Worker settings
worker_class = "sync"
timeout = 120