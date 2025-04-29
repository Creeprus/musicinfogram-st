from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient

User = get_user_model()


class Command(BaseCommand):
    """Команда для создания тестовых данных."""
    help = 'Создает тестовые данные для проекта'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-ingredients',
            action='store_true',
            help='Не загружать ингредиенты'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создание тегов
        tags = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'dinner'},
            {'name': 'Десерт', 'color': '#FF0099', 'slug': 'dessert'},
            {'name': 'Вегетарианское', 'color': '#33CCCC', 'slug': 'vegetarian'}
        ]
        
        for tag_data in tags:
            Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
        
        self.stdout.write(self.style.SUCCESS('Теги созданы'))
        
        # Проверка наличия ингредиентов
        if Ingredient.objects.count() == 0 and not options['no_ingredients']:
            self.stdout.write(
                'Ингредиенты отсутствуют. '
                'Воспользуйтесь командой import_ingredients для их загрузки.'
            )
            return
        
        # Создание пользователей
        users = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'first_name': 'Админ',
                'last_name': 'Админов',
                'password': 'admin'
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
        
        # Создание рецептов
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
                    ],
                    'tags': [Tag.objects.get(slug='breakfast')]
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
                    ],
                    'tags': [Tag.objects.get(slug='lunch'), Tag.objects.get(slug='dinner')]
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
                    ],
                    'tags': [Tag.objects.get(slug='lunch')]
                }
            ]
            
            for recipe_data in recipes_data:
                recipe = Recipe.objects.create(
                    name=recipe_data['name'],
                    text=recipe_data['text'],
                    cooking_time=recipe_data['cooking_time'],
                    author=recipe_data['author']
                )
                
                # Добавление тегов
                recipe.tags.set(recipe_data['tags'])
                
                # Добавление ингредиентов
                recipe_ingredients = []
                for ingredient, amount in recipe_data['ingredients']:
                    recipe_ingredients.append(
                        RecipeIngredient(
                            recipe=recipe,
                            ingredient=ingredient,
                            amount=amount
                        )
                    )
                RecipeIngredient.objects.bulk_create(recipe_ingredients)
                
            self.stdout.write(self.style.SUCCESS('Рецепты созданы'))
        
        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы')
        ) 