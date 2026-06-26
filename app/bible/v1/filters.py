import django_filters

from app.bible.models import Bible


class BibleFilter(django_filters.FilterSet):
    translation = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Bible
        fields = ["translation"]
