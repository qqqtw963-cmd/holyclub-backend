from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.screen_time.models import DailyScreenTimeLog
from app.screen_time.v1.permissions import ScreenTimePermission
from app.screen_time.v1.serializers import DailyScreenTimeLogSerializer


@extend_schema_view(create=extend_schema(summary="스크린타임 수동 입력 (upsert)"))
class DailyScreenTimeLogViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = DailyScreenTimeLog.objects.all()
    serializer_class = DailyScreenTimeLogSerializer
    permission_classes = [ScreenTimePermission]
    pagination_class = None
    filterset_class = None
