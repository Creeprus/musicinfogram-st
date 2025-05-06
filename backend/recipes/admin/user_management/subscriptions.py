from django.contrib import admin
from recipes.models import Subscription


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
