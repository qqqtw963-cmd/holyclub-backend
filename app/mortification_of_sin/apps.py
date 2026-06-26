from django.apps import AppConfig


class MortificationOfSinConfig(AppConfig):
    name = "app.mortification_of_sin"

    def ready(self):
        import app.mortification_of_sin.signals
