from django.apps import AppConfig


class InquiryConfig(AppConfig):
    name = "app.inquiry"

    def ready(self):
        import app.inquiry.signals
