from django.contrib import admin
from recipes.models import Ingredient


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
