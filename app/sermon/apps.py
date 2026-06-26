from django.apps import AppConfig


class SermonConfig(AppConfig):
    name = "app.sermon"
    verbose_name = "C. 설교 관리"

    def ready(self):
        pass
