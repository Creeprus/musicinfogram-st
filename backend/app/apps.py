from django.apps import AppConfig


class AppConfig(AppConfig):
    """Класс конфигурации приложения."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'App'

    def ready(self):
        """Импортирование сигналов и админки."""
        import app.models.signals
        import app.admin
