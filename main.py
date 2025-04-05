import os
import django
from django.core.wsgi import get_wsgi_application

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# Create the WSGI application
app = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5000'])