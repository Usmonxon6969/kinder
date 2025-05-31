#!/bin/sh

# Wait for the database to be ready
echo "Waiting for database..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done
echo "Database is ready!"

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create default superuser if not exists
echo "Checking for superuser..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())" | grep -q "True"
SUPERUSER_EXISTS=$?

if [ $SUPERUSER_EXISTS -ne 0 ]; then
  echo "Creating superuser with admin role..."
  # Use a custom Python script to create the superuser with admin role
  python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    user = User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    );
    user.role = 'admin';
    user.save();
    print('Superuser created with admin role.');
  "
else
  echo "Superuser already exists."
fi

# Execute the CMD
exec "$@"