from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.bible_reading_status.models import BibleReadingStatus
from app.bible_reading_status.v1.filters import BibleReadingStatusFilter
from app.bible_reading_status.v1.permissions import BibleReadingStatusPermission
from app.bible_reading_status.v1.serializers import BibleReadingStatusSerializer
from app.common.pagination import CursorPagination
from app.common.validators import validate_view_request_user


@extend_schema_view(
    list=extend_schema(summary="성경 읽은 상태 목록 조회"),
    create=extend_schema(summary="읽은 성경 등록(계속 등록 가능)"),
    retrieve=extend_schema(summary="성경 읽은 상태 상세 조회"),
    # destroy=extend_schema(summary="읽은 성경 기록 삭제"),
)
class BibleReadingStatusViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    # mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = BibleReadingStatus.objects.all()
    serializer_class = BibleReadingStatusSerializer
    permission_classes = [BibleReadingStatusPermission]
    pagination_class = CursorPagination
    filterset_class = BibleReadingStatusFilter
    ordering = ["book", "chapter"]

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)
        return queryset.filter(user=request_user)
