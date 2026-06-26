from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from app.bible.models import Bible
from app.bible.v1.filters import BibleFilter
from app.bible.v1.serializers import BibleSerializer


@extend_schema_view(
    retrieve=extend_schema(summary="성경 상세 조회"),
)
class BibleViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Bible.objects.all()
    serializer_class = BibleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = BibleFilter
    lookup_url_kwarg = "me"
    lookup_value_regex = "me"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related("version_set")
        return queryset

    def get_object(self):
        return self.get_queryset().first()
