from django.apps import AppConfig


class AppConfig(AppConfig):
    """Класс конфигурации приложения."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Recipes'
