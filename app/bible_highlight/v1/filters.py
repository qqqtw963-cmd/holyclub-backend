import django_filters

from app.bible.utils import BibleBookType
from app.bible_highlight.models import BibleHighlight


class BibleHighlightFilter(django_filters.FilterSet):
    book = django_filters.ChoiceFilter(
        # required=True,
        choices=BibleBookType.choices,
    )
    chapter = django_filters.NumberFilter(
        # required=True,
    )

    class Meta:
        model = BibleHighlight
        fields = [
            "book",
            "chapter",
        ]
