from django.db import OperationalError, ProgrammingError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.home_content.models import HomeContent
from app.home_content.v1.permissions import HomeContentPermission
from app.home_content.v1.serializers import HomeContentSerializer


@extend_schema_view(
    list=extend_schema(summary="홈 콘텐츠 목록 조회"),
    current=extend_schema(summary="현재 활성 홈 콘텐츠 조회"),
)
class HomeContentViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = HomeContent.objects.all()
    serializer_class = HomeContentSerializer
    permission_classes = [HomeContentPermission]
    pagination_class = None

    def get_queryset(self):
        return super().get_queryset().order_by("-is_active", "-updated_at", "-created_at")

    @staticmethod
    def _get_default_payload():
        return {
            "eyebrow": "하나님과 더 가까워지는 거룩한 습관",
            "main_title": "신앙이 자꾸 끊기는 이유는 흩어져 있기 때문입니다.",
            "sub_title": "HolyClub은 말씀, 기도, 묵상, 기록을 하나의 리듬으로 묶어 신앙이 습관이 되도록 돕습니다.",
            "highlight_text": "흩어진 신앙을 다시 하나로",
            "cta_text": "출시 소식 보기",
            "cta_link": "https://holyclub.co.kr/#start",
            "is_active": False,
        }

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request, *args, **kwargs):
        try:
            current_content = self.get_queryset().filter(is_active=True).first() or self.get_queryset().first()
        except (ProgrammingError, OperationalError):
            return Response(self._get_default_payload())

        if current_content is None:
            return Response(self._get_default_payload())

        serializer = self.get_serializer(current_content)
        return Response(serializer.data)
