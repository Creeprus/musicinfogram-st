from django.contrib import admin
from recipes.models import Favorite, ShoppingCart


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
