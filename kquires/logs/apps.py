from django.apps import AppConfig

class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kquires.logs'

    def ready(self):
        # Import signals to connect login/logout handlers
        import kquires.logs.signals
