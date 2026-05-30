#!/bin/bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser using environment variables
if [[ $CREATE_SUPERUSER ]]; then
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model;
User = get_user_model();
username = '${DJANGO_SUPERUSER_USERNAME}'
email = '${DJANGO_SUPERUSER_EMAIL}'
password = '${DJANGO_SUPERUSER_PASSWORD}'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully!')
else:
    print(f'Superuser {username} already exists')
EOF
    echo "Superuser creation attempted."
fi