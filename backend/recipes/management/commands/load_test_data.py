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
            '--no-ingredients',
            action='store_true',
            help='Не загружать ингредиенты'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Функция handler."""
        self.stdout.write('Создание тестовых данных...')

        if Ingredient.objects.count() == 0 and not options['no_ingredients']:
            self.stdout.write(
                'Ингредиенты отсутствуют. '
                'Воспользуйтесь командой import_ingredients для их загрузки.'
            )
            return

        users = [
            {
                'username': 'Pepega',
                'email': 'pepega@example.com',
                'first_name': 'Pepega',
                'last_name': 'PepegaLord',
                'password': 'pepega'
            },
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'password': 'user1pass'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'first_name': 'Петр',
                'last_name': 'Петров',
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

        if not options['no_ingredients'] and Ingredient.objects.exists():
            # Получаем первые несколько ингредиентов для тестовых рецептов
            ingredients = list(Ingredient.objects.all()[:20])

            recipes_data = [
                {
                    'name': 'Омлет с сыром',
                    'text': (
                        'Яичница-болтунья с добавлением сыра. '
                        'Классический завтрак. '
                        'Быстро и вкусно.'
                    ),
                    'cooking_time': 10,
                    'author': created_users[0],
                    'ingredients': [
                        (ingredients[0], 2),
                        (ingredients[1], 100),
                        (ingredients[2], 20)
                    ]
                },
                {
                    'name': 'Паста карбонара',
                    'text': (
                        'Классическая итальянская паста с беконом, '
                        'яйцами и сыром пармезан. '
                        'Быстрое и сытное блюдо.'
                    ),
                    'cooking_time': 30,
                    'author': created_users[1],
                    'ingredients': [
                        (ingredients[3], 200),
                        (ingredients[4], 100),
                        (ingredients[5], 50),
                        (ingredients[6], 2)
                    ]
                },
                {
                    'name': 'Салат "Цезарь"',
                    'text': (
                        'Знаменитый салат с курицей, сухариками, '
                        'салатом романо и заправкой на основе анчоусов. '
                        'Отличный выбор для легкого обеда.'
                    ),
                    'cooking_time': 20,
                    'author': created_users[2],
                    'ingredients': [
                        (ingredients[7], 100),
                        (ingredients[8], 150),
                        (ingredients[9], 50),
                        (ingredients[10], 30)
                    ]
                }
            ]

            for recipe_data in recipes_data:
                recipe = Recipe.objects.create(
                    name=recipe_data['name'],
                    text=recipe_data['text'],
                    cooking_time=recipe_data['cooking_time'],
                    author=recipe_data['author']
                )

                recipe_ingredients = []
                for ingredient, amount in recipe_data['ingredients']:
                    recipe_ingredients.append(
                        IngredientInRecipe(
                            recipe=recipe,
                            ingredient=ingredient,
                            amount=amount
                        )
                    )
                IngredientInRecipe.objects.bulk_create(recipe_ingredients)

            self.stdout.write(self.style.SUCCESS('Рецепты созданы'))

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы')
        )
