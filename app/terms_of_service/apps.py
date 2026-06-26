from django.apps import AppConfig


class TermsOfServiceConfig(AppConfig):
    name = "app.terms_of_service"
    verbose_name = "E. 이용 약관 관리"

    def ready(self):
        pass
