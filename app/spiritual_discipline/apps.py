from django.apps import AppConfig


class SpiritualDisciplineConfig(AppConfig):
    name = "app.spiritual_discipline"

    def ready(self):
        import app.spiritual_discipline.signals
