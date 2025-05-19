#!/bin/bash
echo "Ожидание базы..."
sleep 2

python prepare_fonts.py

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput
echo "Создание суперюзера..."
python manage.py createsuperuser --noinput --username "admin" --email "admin@example.com" --first_name "admin" --last_name "admin"
if [ -f "data/genres.json" ]; then
    python manage.py import_genres data/genres.json
    python manage.py load_test_data
fi

gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 