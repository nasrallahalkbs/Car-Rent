import os
import logging

from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import views after app is created to avoid circular imports
from views import *
from admin import admin_blueprint

# Register blueprints
app.register_blueprint(admin_blueprint, url_prefix='/admin')

# Import models after app is created
from models import User

@login_manager.user_loader
def load_user(user_id):
    from models import users
    return users.get(int(user_id))
