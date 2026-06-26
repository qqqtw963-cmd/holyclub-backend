from collections import defaultdict

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.bible_reading_log.models import BibleReadingLog
from app.bible_reading_log.v1.filters import BibleReadingLogFilter
from app.bible_reading_log.v1.permissions import BibleReadingLogPermission
from app.bible_reading_log.v1.serializers import BibleReadingLogListSerializer, BibleReadingLogSerializer
from app.common.pagination import CursorPagination
from app.common.validators import validate_view_request_user


@extend_schema_view(
    list=extend_schema(
        summary="(데일리)성경 읽기 기록 목록 조회",
        responses={200: OpenApiResponse(response=BibleReadingLogListSerializer)},
    ),
    create=extend_schema(summary="(데일리)성경 읽기 기록 등록"),
)
class BibleReadingLogViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = BibleReadingLog.objects.all()
    serializer_class = BibleReadingLogSerializer
    permission_classes = [BibleReadingLogPermission]
    pagination_class = CursorPagination
    filterset_class = BibleReadingLogFilter
    ordering = ["recognized_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return BibleReadingLogListSerializer
        return BibleReadingLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)
        return queryset.filter(user=request_user)

    def list(self, request, *args, **kwargs):
        """성경 읽기 기록 목록 조회"""
        queryset = self.filter_queryset(self.get_queryset())

        total_count = queryset.count()
        total_reading_count = sum(log.count for log in queryset)

        results = []
        for log in queryset:
            results.append(
                {
                    "id": log.id,
                    "count": log.count,
                    "local_date": log.local_date,
                    "recognized_date": log.recognized_date,
                    "created_at": log.created_at,
                }
            )

        response_data = {
            "count": total_count,
            "today_total_chapter_count": total_reading_count,
            "results": results,
        }

        return Response(response_data)
