from django.apps import AppConfig


class BibleReadingLogConfig(AppConfig):
    name = "app.bible_reading_log"

    def ready(self):
        import app.bible_reading_log.signals
