import django_filters

from app.prayer_journal.models import PrayerJournal


class PrayerJournalFilter(django_filters.FilterSet):
    is_answered = django_filters.BooleanFilter()

    class Meta:
        model = PrayerJournal
        fields = ["is_answered"]
