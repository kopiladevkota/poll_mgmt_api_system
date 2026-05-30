#!/bin/bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='kopila').exists():
    User.objects.create_superuser('kopila', 'kopiladevkot7@gmail.com', '1234')
    print('✅ Superuser "kopila" created!')
else:
    print('✅ Superuser "kopila" already exists.')
EOF

echo "Build completed!"