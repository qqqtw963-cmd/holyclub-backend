from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import CursorPagination
from app.common.validators import validate_view_request_user
from app.pray_time_log.models import PrayTimeLog
from app.pray_time_log.v1.filters import PrayTimeLogFilter
from app.pray_time_log.v1.permissions import PrayTimeLogPermission
from app.pray_time_log.v1.serializers import PrayTimeLogSerializer


@extend_schema_view(
    list=extend_schema(summary="(하루의) 기도 시간 목록 조회"),
    create=extend_schema(summary="(하루의) 기도 시간 등록"),
    destroy=extend_schema(summary="(하루의) 기도 시간 삭제"),
)
class PrayTimeLogViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = PrayTimeLog.objects.all()
    serializer_class = PrayTimeLogSerializer
    permission_classes = [PrayTimeLogPermission]
    pagination_class = CursorPagination
    filterset_class = PrayTimeLogFilter
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)
        return queryset.filter(user=request_user)
