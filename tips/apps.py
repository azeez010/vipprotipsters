from django.apps import AppConfig


class TipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tips'

    def ready(self):
        # import signal handlers
        import tips.signals
