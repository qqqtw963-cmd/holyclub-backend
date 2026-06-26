from django.apps import AppConfig


class PrayTimeLogConfig(AppConfig):
    name = "app.pray_time_log"

    def ready(self):
        import app.pray_time_log.signals
