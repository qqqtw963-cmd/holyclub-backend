from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "app.notification"
    verbose_name = "D. 공지 및 문의 관리"

    def ready(self):
        pass
