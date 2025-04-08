#!/bin/bash
# Kill any running Django server
ps aux | grep "runserver" | grep -v grep | awk '{print $2}' | xargs -r kill -9
# Start the Django development server
python manage.py runserver 0.0.0.0:8000