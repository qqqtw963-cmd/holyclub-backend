from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import CursorPagination
from app.prayer_bgm_track.models import PrayerBgmListeningState, PrayerBgmTrack
from app.prayer_bgm_track.v1.filters import PrayerBgmListeningStateFilter, PrayerBgmTrackFilter
from app.prayer_bgm_track.v1.permissions import PrayerBgmListeningStatePermission, PrayerBgmTrackPermission
from app.prayer_bgm_track.v1.serializers import PrayerBgmListeningStateSerializer, PrayerBgmTrackSerializer


@extend_schema_view(
    list=extend_schema(summary="기도용 BGM 목록 조회"),
)
class PrayerBgmTrackViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = PrayerBgmTrack.objects.all()
    serializer_class = PrayerBgmTrackSerializer
    permission_classes = [PrayerBgmTrackPermission]
    pagination_class = CursorPagination
    filterset_class = PrayerBgmTrackFilter
    ordering = ["order", "-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


@extend_schema_view(
    create=extend_schema(summary="유저별 기도 BGM 청취, 등록"),  # user별 bgm log
    retrieve=extend_schema(summary="유저별 기도 BGM 청취 현황, 상세 조회"),
)
class PrayerBgmListeningStateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = PrayerBgmListeningState.objects.all()
    serializer_class = PrayerBgmListeningStateSerializer
    permission_classes = [PrayerBgmListeningStatePermission]
    pagination_class = None  # 언제나 단일 객체만 반환 (그러면 아래의 get_queryset 은 필요 없는거 아닌가?)
    filterset_class = PrayerBgmListeningStateFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
