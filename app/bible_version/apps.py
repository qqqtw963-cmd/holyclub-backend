from django.apps import AppConfig


class BibleVersionConfig(AppConfig):
    name = "app.bible_version"

    def ready(self):
        import app.bible_version.signals
