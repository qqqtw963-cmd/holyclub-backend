from django.apps import AppConfig


class BibleConfig(AppConfig):
    name = "app.bible"
    verbose_name = "G. 성경 번역본"

    def ready(self):
        pass
