from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.daily_check_status.models import DailyCheckStatus
from app.daily_check_status.v1.permissions import DailyCheckStatusPermission
from app.daily_check_status.v1.serializers import DailyCheckStatusSerializer


@extend_schema_view(
    list=extend_schema(summary="(예배/산상수훈) 매일 체크 상태 목록 조회 (사용X)"),
    create=extend_schema(summary="(예배/산상수훈) 매일 체크 상태 등록 (on/off)"),
)
class DailyCheckStatusViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = DailyCheckStatus.objects.all()
    serializer_class = DailyCheckStatusSerializer
    permission_classes = [DailyCheckStatusPermission]
    pagination_class = None
    filterset_class = None
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
