#!/bin/sh


su -c "python manage.py makemigrations"

su -c "python manage.py migrate"


su -c "python manage.py runserver 0.0.0.0:8000"
