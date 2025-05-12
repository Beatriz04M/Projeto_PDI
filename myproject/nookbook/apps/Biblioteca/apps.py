from django.apps import AppConfig


class BibliotecaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nookbook.apps.Biblioteca'

    def ready(self):
        import nookbook.apps.Biblioteca.signals
