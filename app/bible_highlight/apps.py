from django.apps import AppConfig


class BibleHighlightConfig(AppConfig):
    name = "app.bible_highlight"

    def ready(self):
        import app.bible_highlight.signals
