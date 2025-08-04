from django.apps import AppConfig

class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kquires.articles'

    def ready(self):
        import kquires.articles.signals  # Import the signals when the app is ready
