#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Prepare fonts for PDF generation
python foodgram/prepare_fonts.py
python foodgram/manage.py makemigrations users
python foodgram/manage.py makemigrations recipes
# Migrate database
python foodgram/manage.py migrate

# Collect static files
python foodgram/manage.py collectstatic --noinput
python foodgram/manage.py shell -c "from users.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

# Import ingredients from JSON file if needed
if [ -f "data/ingredients.json" ]; then
    python foodgram/manage.py import_ingredients data/ingredients.json
    python foodgram/manage.py load_test_data
fi

# Start server
cd foodgram
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 