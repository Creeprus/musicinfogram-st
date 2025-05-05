from django.contrib import admin
from django.utils.safestring import mark_safe
from app.models import Recipe


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
            for ing in obj.ingredients_in_recipe.all()
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
