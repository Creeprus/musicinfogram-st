# Foodgram - «Продуктовый помощник»

[![Foodgram workflow](https://github.com/Creeprus/foodgram-st/actions/workflows/foodgram_workflow.yml)](https://github.com/Creeprus/foodgram-st/actions/workflows/foodgram_workflow.yml)

## Описание проекта

«Продуктовый помощник» — онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Функциональность

- Регистрация пользователей и авторизация
- Создание, редактирование и удаление рецептов (для авторов)
- Просмотр рецептов всеми пользователями
- Подписка на авторов рецептов
- Добавление рецептов в избранное
- Добавление рецептов в список покупок
- Скачивание списка покупок в формате PDF
- Административный интерфейс для управления данными

## Технологии

- Python 3.7
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- GitHub Actions

## Подготовка и запуск проекта

### Предварительные требования

- Docker
- Docker Compose

### Запуск проекта

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/Creeprus/foodgram-st
   cd foodgram-st
   ```

2. Создайте файл .env в директории infra/ и заполните его переменными окружения:
   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   DEBUG=True
   ALLOWED_HOSTS=['127.0.0.1','localhost','backend']
   ```

3. Запустите Docker Compose:
   ```
   cd infra
   docker-compose up -d --build
   ```
Проект при сборке автоматически заполняет базу ингредиентами, тестовыми данными и суперпользователем. При нужде это можно сделать вручную

3. 1. Команда для ручного заполнения: 
   ```
   docker-compose exec backend python manage.py import_ingredients /app/data/ingredients.json 
   ```
3. 2. Команда для заполнения тестовыми данными (могут сразу не отобразится на верстке): 
```
docker-compose exec backend python manage.py load_test_data
```
3. 3. Команда для создания суперпользователя: 
```
docker-compose exec backend python manage.py createsuperuser --noinput --username "admin" --email "admin@example.com" --password "admin" --first_name "admin" --last_name "admin"
```
4. Проект будет доступен по адресу http://localhost/ или 127.0.0.1:80/

5. Админка будет доступна по адресу https://localhost/admin или http://localhost:8000/admin/

### Для разработчиков

1. Установите зависимости в виртуальном окружении:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # для Linux/macOS
   # или
   venv\Scripts\activate     # для Windows
   pip install -r requirements.txt
   ```

2. Запустите проект в режиме разработки:
   ```
   cd foodgram
   python manage.py runserver
   ```

## Документация API

API доступен по адресу http://localhost:80/api/ и документация доступна по адресу http://localhost:80/api/docs/

## Автор

- [Корниенко Лев](https://github.com/Creeprus)
