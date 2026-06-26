from django.apps import AppConfig


class TestimonyJournalConfig(AppConfig):
    name = "app.testimony_journal"

    def ready(self):
        import app.testimony_journal.signals
