from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import CursorPagination
from app.common.validators import validate_view_request_user
from app.prayer_journal.models import PrayerJournal
from app.prayer_journal.v1.filters import PrayerJournalFilter
from app.prayer_journal.v1.permissions import PrayerJournalPermission
from app.prayer_journal.v1.serializers import (
    PrayerJournalAnsweredSerializer,
    PrayerJournalListSerializer,
    PrayerJournalSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="기도제목 목록 조회", responses=PrayerJournalListSerializer),
    create=extend_schema(
        summary="기도제목 등록",
        request=inline_serializer(
            name="PrayerJournalCreate",
            fields={
                "title": serializers.CharField(),
                "content": serializers.CharField(),
                "start_date": serializers.DateField(
                    required=False, help_text="입력하면 해당 값으로 db에 저장하고, 입력값이 없으면 생성일 기준으로 db에 저장되도록"
                ),
            },
        ),
    ),
    retrieve=extend_schema(summary="기도제목 상세 조회"),
    update=extend_schema(
        summary="기도제목 수정",
        request=inline_serializer(
            name="PrayerJournalUpdate",
            fields={
                "title": serializers.CharField(required=False),
                "content": serializers.CharField(required=False),
                "start_date": serializers.DateField(required=False),
                "is_answered": serializers.BooleanField(required=True),
                "answer_date": serializers.DateField(required=False),
            },
        ),
    ),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="기도제목 삭제"),
    answered=extend_schema(summary="기도제목 응답 여부"),
)
class PrayerJournalViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = PrayerJournal.objects.all()
    serializer_class = PrayerJournalSerializer
    permission_classes = [PrayerJournalPermission]
    pagination_class = CursorPagination
    filterset_class = PrayerJournalFilter
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)
        return queryset.filter(user=request_user)

    def get_serializer_class(self):
        if self.action == "list":
            return PrayerJournalListSerializer
        if self.action == "answered":
            return PrayerJournalAnsweredSerializer
        return PrayerJournalSerializer

    @action(methods=["POST"], detail=True, serializer_class=PrayerJournalAnsweredSerializer)
    def answered(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
