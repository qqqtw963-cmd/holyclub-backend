from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.bible_highlight.models import BibleHighlight
from app.bible_highlight.v1.filters import BibleHighlightFilter
from app.bible_highlight.v1.permissions import BibleHighlightPermission
from app.bible_highlight.v1.serializers import BibleHighlightSerializer
from app.common.pagination import CursorPagination
from app.common.validators import validate_view_request_user


@extend_schema_view(
    list=extend_schema(summary="성경 하이라이트 목록 조회"),
    create=extend_schema(summary="성경 하이라이트 등록"),
    destroy=extend_schema(summary="성경 하이라이트 삭제"),
)
class BibleHighlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = BibleHighlight.objects.all()
    serializer_class = BibleHighlightSerializer
    permission_classes = [BibleHighlightPermission]
    pagination_class = CursorPagination
    filterset_class = BibleHighlightFilter
    ordering = ["verse"]

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)
        return queryset.filter(user=request_user)
