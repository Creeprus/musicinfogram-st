from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from recipes.models import User


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
