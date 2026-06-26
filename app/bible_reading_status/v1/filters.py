import django_filters

from app.bible.utils import BibleBookType
from app.bible_reading_status.models import BibleReadingStatus


class BibleReadingStatusFilter(django_filters.FilterSet):
    book = django_filters.ChoiceFilter(
        # required=True,
        choices=BibleBookType.choices,
    )
    chapter = django_filters.NumberFilter(
        # required=True,
    )

    class Meta:
        model = BibleReadingStatus
        fields = [
            "book",
            "chapter",
        ]
