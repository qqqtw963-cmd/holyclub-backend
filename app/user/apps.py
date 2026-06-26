from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "app.user"
    verbose_name = "A. 회원 관리"

    def ready(self):
        pass
