from django.apps import AppConfig


class BibleReadingStatusConfig(AppConfig):
    name = "app.bible_reading_status"

    def ready(self):
        import app.bible_reading_status.signals
