from django.apps import AppConfig


class DailyCheckStatusConfig(AppConfig):
    name = "app.daily_check_status"

    def ready(self):
        import app.daily_check_status.signals
