from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import GenericViewSet

from app.bible_version.models import BibleVersion
from app.bible_version.v1.filters import BibleVersionFilter
from app.bible_version.v1.permissions import BibleVersionPermission
from app.bible_version.v1.serializers import BibleVersionSerializer
from app.common.pagination import CursorPagination


@extend_schema_view(
    list=extend_schema(summary="BibleVersion 목록 조회"),
    create=extend_schema(summary="BibleVersion 등록"),
    retrieve=extend_schema(summary="BibleVersion 상세 조회"),
    update=extend_schema(summary="BibleVersion 수정"),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="BibleVersion 삭제"),
)
class BibleVersionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = BibleVersion.objects.all()
    serializer_class = BibleVersionSerializer
    permission_classes = [BibleVersionPermission]
    pagination_class = CursorPagination
    filterset_class = BibleVersionFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    # 특정 action에 다른 Filter를 설정해야하는 경우 사용
    def get_filterset_class(self):
        return getattr(self, "filterset_class", None)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("patch")
