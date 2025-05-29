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
    @admin.display(description='Тип')
    def get_model_name(self, obj):
        """
        Функция, определяющая тип (избранное или в корзине).

        :param obj: Объект модели
        :returns: Название модели, к которой относится запись
        """
        return 'Избранное' if isinstance(obj, Favorite) else 'Корзина покупок'

    list_display = ('id', 'user', 'recipe', 'get_model_name', 'created_at')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    list_filter = ('user', 'recipe__author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Класс, для работы с ингредиентами (админ).

    :param list_display: Поля, отображаемые в списке жанров
    :param list_filter: Поля для фильтрации жанров
    :param search_fields: Поля, по которым можно осуществлять поиск
    :param ordering: Порядок сортировки жанров
    """

    list_display = ('id', 'name', 'measurement_unit', 'get_recipe_count')
    list_filter = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)

    @admin.display(description='Используется в альбомах')
    def get_recipe_count(self, obj):
        """
        Функция, которая подсчитывает количество альбомов,
        в котором используется данный жанр.

        :params obj: Объект жанра
        :returns: Количество рецептов с данным жанров
        """
        return obj.recipe_ingredients.count()


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Класс, для справочной сущности IngredientRecipe (админ)."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


class IngredientInRecipeInline(admin.TabularInline):
    """Inline класс для GenresInAlbum."""

    model = IngredientInRecipe
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Класс, для работы с альбомами (админ).

    :param list_display: Поля, отображаемые в списке альбомов
    :param search_fields: Поля, по которым можно осуществлять поиск
    :param list_filter: Поля для фильтрации альбомов
    :param ordering: Порядок сортировки альбомов
    """

    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        # 'get_favorites_count',
        'get_ingredients_display',
        'get_image_display',
        'created_at',
    )

    inlines = [IngredientInRecipeInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    @admin.display(description='Жанры')
    def get_ingredients_display(self, obj):
        """
        Функция, которая возвращает список жанров,
        используемых в рецепте.

        :param obj: Объект рецепта
        :returns: HTML-строка с форматированным списком жанров
        """
        return mark_safe('<br>'.join([
            f'{ing.ingredient.name} - {ing.amount} '
            f'{ing.ingredient.measurement_unit}'
            for ing in obj.recipe_ingredients.all()
        ]))

    @admin.display(description='Картинка')
    def get_image_display(self, obj):
        """
        Функция, которая возвращает изображение альбома.

        :param obj: Объект альбома
        :returns: HTML-тег img или текст, если изображение отсутствует
        """
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" '
                'width="50" height="50" />'
            )
        return 'Нет изображения'

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        """
        Функция, которая подсчитывает количество пользователей,
        добавивших рецепт в избранное.

        :param obj: Объект рецепта
        :Returns: Количество пользователей, добавивших рецепт в избранное
        """
        return obj.favorites.count()

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

    @admin.display(description='ФИО')
    def get_full_name_display(self, obj):
        """Отображает полное имя пользователя (ФИО)"""
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description='Аватар')
    def get_avatar_display(self, obj):
        """Отображает аватар пользователя в виде миниатюры"""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" />'
            )
        return 'Нет аватара'

    @admin.display(description='Количество альбомов')
    def get_recipe_count(self, obj):
        """Подсчитывает количество рецептов пользователя"""
        return obj.recipes.count()

    @admin.display(description='Количество подписок')
    def get_subscriptions_count(self, obj):
        """Подсчитывает количество подписок пользователя"""
        return obj.users.count()

    @admin.display(description='Количество подписчиков')
    def get_subscribers_count(self, obj):
        """Подсчитывает количество подписчиков пользователя"""
        return obj.authors.count()

    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('id',)
    readonly_fields = ('date_joined', 'last_login')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Административная панель для управления подписками пользователей.
    Предоставляет интерфейс для управления подписками пользователей
    на авторов альбомов.
    Attributes:
        list_display: Поля, отображаемые в списке подписок
        search_fields: Поля, по которым можно осуществлять поиск
        list_filter: Поля для фильтрации подписок
        ordering: Порядок сортировки подписок
    """

    list_display = (
        'id',
        'user',
        'author',
        'get_author_recipes_count',
        'created_at'
    )

    @admin.display(description='Альбомы у автора')
    def get_author_recipes_count(self, obj):
        """
        Подсчитывает количество альбомов автора.
        Args:
            obj: Объект подписки
        Returns:
            Количество рецептов автора
        """
        return obj.author.recipes.count()

    search_fields = (
        'user__email',
        'user__username',
        'author__email',
        'author__username'
    )
    list_filter = ('user', 'author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
