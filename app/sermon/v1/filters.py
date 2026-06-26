import django_filters

from app.common.validators import validate_view_request_user
from app.sermon.models import OvernightWorshipType, Sermon, SermonBookmark, WorshipType

"""
필터링
	테이블의 id로 필터링 가능하도록
	(다른 것 취소) 북마크 여부
"""


class SermonFilter(django_filters.FilterSet):
    worship_type = django_filters.ChoiceFilter(
        field_name="worship_type",
        choices=WorshipType.choices,
        label="북마크 필터링을 위해 선택값으로 둠",
    )

    sunday_preacher = django_filters.NumberFilter(
        field_name="sunday_preacher__id",
    )
    overnight_worship_type = django_filters.ChoiceFilter(
        field_name="overnight_worship_type",
        choices=OvernightWorshipType.choices,
    )

    is_bookmarked = django_filters.BooleanFilter(
        method="filter_is_bookmarked",
    )

    class Meta:
        model = Sermon
        fields = [
            "worship_type",
            "sunday_preacher",
            "overnight_worship_type",
            "is_bookmarked",
        ]

    def filter_is_bookmarked(self, queryset, name, value):
        user = validate_view_request_user(self.request)
        bookmarked_sermon_ids = SermonBookmark.objects.filter(user=user).values_list("sermon_id", flat=True)
        if value:
            return queryset.filter(id__in=bookmarked_sermon_ids)
        else:
            return queryset.exclude(id__in=bookmarked_sermon_ids)
