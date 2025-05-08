from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Favorite, ShoppingCart,
    IngredientInRecipe, Ingredient,
    Recipe, User, Subscription)
from django.utils.safestring import mark_safe


@admin.register(Favorite, ShoppingCart)
class FavoriteAndShoppingCartAdmin(admin.ModelAdmin):
    """
    Класс для работы с избранными товарами и товарами в корзине (админ).

    :param list_display: Поля отображаемые в списке записей
    :param search_fields: Поля, по которым можно осуществлять поиск
    :param list_filter: Поля для фильтрации записей
    :param ordering: Порядок сортировки записей
    """

    def get_model_name(self, obj):
        """
        Функция, определяющая тип (избранное или в корзине).

        :param obj: Объект модели
        :returns: Название модели, к которой относится запись
        """
        return 'Избранное' if isinstance(obj, Favorite) else 'Корзина покупок'
    get_model_name.short_description = 'Тип'

    list_display = ('id', 'user', 'recipe', 'get_model_name', 'created_at')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    list_filter = ('user', 'recipe__author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Класс, для работы с ингредиентами (админ).

    :param list_display: Поля, отображаемые в списке ингредиентов
    :param list_filter: Поля для фильтрации ингредиентов
    :param search_fields: Поля, по которым можно осуществлять поиск
    :param ordering: Порядок сортировки ингредиентов
    """

    list_display = ('id', 'name', 'measurement_unit', 'get_recipe_count')
    list_filter = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)

    def get_recipe_count(self, obj):
        """
        Функция, которая подсчитывает количество рецептов,
        в котором используется данный игредиент.

        :params obj: Объект ингредиента
        :returns: Количество рецептов с данным ингредиентом
        """
        return obj.recipe_ingredients.count()
    get_recipe_count.short_description = 'Используется в рецептах'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Класс, для справочной сущности IngredientRecipe (админ)."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Класс, для работы с рецептами (админ).

    :param list_display: Поля, отображаемые в списке рецептов
    :param search_fields: Поля, по которым можно осуществлять поиск
    :param list_filter: Поля для фильтрации рецептов
    :param ordering: Порядок сортировки рецептов
    """

    def get_ingredients_display(self, obj):
        """
        Функция, которая возвращает список ингредиентов,
        используемых в рецепте.

        :param obj: Объект рецепта
        :returns: HTML-строка с форматированным списком ингредиентов
        """
        return mark_safe('<br>'.join([
            f'{ing.ingredient.name} - {ing.amount} '
            f'{ing.ingredient.measurement_unit}'
            for ing in obj.recipe_ingredients.all()
        ]))
    get_ingredients_display.short_description = 'Продукты'

    def get_image_display(self, obj):
        """
        Функция, которая возвращает изображение рецепта.

        :param obj: Объект рецепта
        :returns: HTML-тег img или текст, если изображение отсутствует
        """
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" '
                'width="50" height="50" />'
            )
        return 'Нет изображения'
    get_image_display.short_description = 'Картинка'

    def get_favorites_count(self, obj):
        """
        Функция, которая подсчитывает количество пользователей,
        добавивших рецепт в избранное.

        :param obj: Объект рецепта
        :Returns: Количество пользователей, добавивших рецепт в избранное
        """
        return obj.favorites.count()
    get_favorites_count.short_description = 'В избранном'

    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'get_favorites_count',
        'get_ingredients_display',
        'get_image_display',
        'created_at',
    )
    search_fields = ('name', 'author__username', 'author__email', 'text')
    list_filter = ('author', 'created_at', 'cooking_time')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    filter_horizontal = ('ingredients',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Административная панель для управления пользователями.
    Наследуется от BaseUserAdmin Django для базовой функциональности.
    Добавляет дополнительные поля и методы
    для отображения информации о пользователях.
    Attributes:
        list_display: Поля, отображаемые в списке пользователей
        search_fields: Поля, по которым можно осуществлять поиск
        ordering: Порядок сортировки пользователей
    """

    def get_full_name_display(self, obj):
        """Отображает полное имя пользователя (ФИО)"""
        return f"{obj.first_name} {obj.last_name}"
    get_full_name_display.short_description = 'ФИО'

    def get_avatar_display(self, obj):
        """Отображает аватар пользователя в виде миниатюры"""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" />'
            )
        return 'Нет аватара'
    get_avatar_display.short_description = 'Аватар'

    def get_recipe_count(self, obj):
        """Подсчитывает количество рецептов пользователя"""
        return obj.recipes.count()
    get_recipe_count.short_description = 'Рецептов'

    def get_subscriptions_count(self, obj):
        """Подсчитывает количество подписок пользователя"""
        return obj.users.count()
    get_subscriptions_count.short_description = 'Подписок'

    def get_subscribers_count(self, obj):
        """Подсчитывает количество подписчиков пользователя"""
        return obj.authors.count()
    get_subscribers_count.short_description = 'Подписчиков'

    list_display = (
        'id',
        'username',
        'get_full_name_display',
        'email',
        'get_avatar_display',
        'get_recipe_count',
        'get_subscriptions_count',
        'get_subscribers_count',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('id',)
    readonly_fields = ('date_joined', 'last_login')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Административная панель для управления подписками пользователей.
    Предоставляет интерфейс для управления подписками пользователей
    на авторов рецептов.
    Attributes:
        list_display: Поля, отображаемые в списке подписок
        search_fields: Поля, по которым можно осуществлять поиск
        list_filter: Поля для фильтрации подписок
        ordering: Порядок сортировки подписок
    """

    def get_author_recipes_count(self, obj):
        """
        Подсчитывает количество рецептов автора.
        Args:
            obj: Объект подписки
        Returns:
            Количество рецептов автора
        """
        return obj.author.recipes.count()
    get_author_recipes_count.short_description = 'Рецептов у автора'

    list_display = (
        'id',
        'user',
        'author',
        'get_author_recipes_count',
        'created_at'
    )
    search_fields = (
        'user__email',
        'user__username',
        'author__email',
        'author__username'
    )
    list_filter = ('user', 'author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
