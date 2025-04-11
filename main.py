import os
import django
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# Create the WSGI application
# Use StaticFilesHandler in development to serve static files
application = StaticFilesHandler(get_wsgi_application())
app = application

# Make sure static files are collected
if not os.path.exists(settings.STATIC_ROOT):
    os.system('python manage.py collectstatic --noinput')

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    port = int(os.environ.get("PORT", 8000))
    execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])