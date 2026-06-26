from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import LimitOffsetPagination
from app.common.validators import validate_view_request_user
from app.testimony_journal.models import TestimonyJournal
from app.testimony_journal.v1.filters import TestimonyJournalFilter
from app.testimony_journal.v1.permissions import TestimonyJournalPermission
from app.testimony_journal.v1.serializers import TestimonyJournalSerializer


@extend_schema_view(
    list=extend_schema(summary="고백록 목록 조회"),
    create=extend_schema(summary="고백록 등록"),
    retrieve=extend_schema(summary="고백록 상세 조회"),
    update=extend_schema(summary="고백록 수정"),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="고백록 삭제"),
)
class TestimonyJournalViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = TestimonyJournal.objects.all()
    serializer_class = TestimonyJournalSerializer
    permission_classes = [TestimonyJournalPermission]
    pagination_class = LimitOffsetPagination
    filterset_class = TestimonyJournalFilter
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)
        queryset = queryset.filter(user=request_user)
        # todo 작성자만 조회할 수 있도록
        return queryset
