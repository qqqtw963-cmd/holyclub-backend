from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import LimitOffsetPagination
from app.notification.models import Notification
from app.notification.v1.filters import NotificationFilter
from app.notification.v1.permissions import NotificationPermission
from app.notification.v1.serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(summary="공지사항 목록 조회"),
    retrieve=extend_schema(summary="공지사항 상세 조회"),
)
class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [NotificationPermission]
    pagination_class = LimitOffsetPagination
    filterset_class = NotificationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
