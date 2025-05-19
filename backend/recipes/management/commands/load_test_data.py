from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from recipes.models import Ingredient, Recipe, IngredientInRecipe

User = get_user_model()


class Command(BaseCommand):
    """Класс, в котором описана команда импортирования тестовых
    данных для manage.py"""
    help = 'Создает тестовые данные для проекта'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-genres',
            action='store_true',
            help='Не загружать жанры'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Функция handler."""
        self.stdout.write('Создание тестовых данных...')

        if Ingredient.objects.count() == 0 and not options['no_genres']:
            self.stdout.write(
                'Ингредиенты отсутствуют. '
                'Воспользуйтесь командой import_genres для их загрузки.'
            )
            return

        users = [
            {
                'username': 'Pepega',
                'email': 'pepega@example.com',
                'first_name': 'Invader',
                'last_name': '303',
                'password': 'pepega'
            },
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': 'Hideaki',
                'last_name': 'Kobayashi',
                'password': 'user1pass'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'first_name': 'Lyn',
                'last_name': 'Inaizumi',
                'password': 'user2pass'
            }
        ]

        created_users = []
        for user_data in users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
            created_users.append(user)

        self.stdout.write(self.style.SUCCESS('Пользователи созданы'))

        if not options['no_genres'] and Ingredient.objects.exists():
            genres = list(Ingredient.objects.all()[:20])

            albums_data = [
                {
                    'name': 'SANABI',
                    'text': (
                        'Executing The King Order\n'
                        'SANABI'
                    ),
                    'cooking_time': 120,
                    'author': created_users[0],
                    'genres': [
                        (genres[0], 2),
                        (genres[1], 2),
                        (genres[2], 3)
                    ]
                },
                {
                    'name': 'Like A Dragon: Gaiden',
                    'text': (
                        'Bring It On\n'
                        'Obediance '
                    ),
                    'cooking_time': 12,
                    'author': created_users[1],
                    'genres': [
                        (genres[3], 2),
                        (genres[4], 3),
                        (genres[5], 4),
                        (genres[6], 2)
                    ]
                },
                {
                    'name': 'Persona 5 Royal',
                    'text': (
                        'I Believe\n'
                        'Last Surprise\n'
                        'Takeover'
                    ),
                    'cooking_time': 20,
                    'author': created_users[2],
                    'genres': [
                        (genres[7], 100),
                        (genres[8], 150),
                        (genres[9], 50),
                        (genres[10], 30)
                    ]
                }
            ]

            for album_data in albums_data:
                album = Recipe.objects.create(
                    name=album_data['name'],
                    text=album_data['text'],
                    cooking_time=album_data['cooking_time'],
                    author=album_data['author']
                )

                album_genres = []
                for ingredient, amount in album_data['genres']:
                    album_genres.append(
                        IngredientInRecipe(
                            recipe=album,
                            ingredient=ingredient,
                            amount=amount
                        )
                    )
                IngredientInRecipe.objects.bulk_create(album_genres)

            self.stdout.write(self.style.SUCCESS('Альбомы созданы'))

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы')
        )
