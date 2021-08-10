#!/usr/bin/env bash

python manage.py collectstatic --no-input --clear
python manage.py makemigrations
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.count() == 0 and User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')" | python manage.py shell

gunicorn quizes.wsgi:application --workers=2 --bind 0.0.0.0:8001
