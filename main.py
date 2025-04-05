from wsgi import app

if __name__ == "__main__":
    # This file is only used when debugging the application directly
    # For production, gunicorn will import the app directly
    from django.core.management import execute_from_command_line
    import os
    import sys
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)
