import django_filters

from app.testimony_journal.models import TestimonyJournal


class TestimonyJournalFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name="created_at__date")
    # created_at_after = django_filters.DateFilter(field_name="created_at__date", lookup_expr="gte")
    # created_at_before = django_filters.DateFilter(field_name="created_at__date", lookup_expr="lte")
    search = django_filters.CharFilter(field_name="content", lookup_expr="icontains")

    class Meta:
        model = TestimonyJournal
        fields = [
            "created_at",
            # "created_at_after",
            # "created_at_before",
            "search",
        ]
