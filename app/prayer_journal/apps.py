from django.apps import AppConfig


class PrayerJournalConfig(AppConfig):
    name = "app.prayer_journal"

    def ready(self):
        import app.prayer_journal.signals
