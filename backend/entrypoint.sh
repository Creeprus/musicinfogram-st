#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Prepare fonts for PDF generation
python foodgram/prepare_fonts.py

# Migrate database
python foodgram/manage.py migrate

# Collect static files
python foodgram/manage.py collectstatic --noinput

# Create superuser if needed
if [ "${DJANGO_SUPERUSER_USERNAME}" ]; then
    python foodgram/manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL \
        || true
fi

# Import ingredients from JSON file if needed
if [ -f "data/ingredients.json" ]; then
    python foodgram/manage.py import_ingredients data/ingredients.json
fi

# Start server
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 