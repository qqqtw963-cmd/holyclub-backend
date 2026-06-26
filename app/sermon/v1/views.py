from django.db import models
from django.db.models import Case, Exists, OuterRef, Value, When
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import CursorPagination
from app.common.validators import validate_view_request_user
from app.sermon.models import Sermon, SermonBookmark, SermonWatch
from app.sermon.v1.filters import SermonFilter
from app.sermon.v1.permissions import SermonPermission
from app.sermon.v1.serializers import SermonBookmarkSerializer, SermonSerializer, SermonWatchSerializer


@extend_schema_view(
    list=extend_schema(summary="설교 목록 조회"),
    retrieve=extend_schema(summary="설교 상세 조회"),
    bookmark=extend_schema(summary="설교 북마크 (on/off)"),
    watch=extend_schema(summary="설교 시청 (on/off)"),
)
class SermonViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Sermon.objects.all()
    serializer_class = SermonSerializer
    permission_classes = [SermonPermission]
    pagination_class = CursorPagination  # done
    filterset_class = SermonFilter
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = validate_view_request_user(self.request)

        queryset = queryset.annotate(
            is_watched=Case(
                When(
                    Exists(
                        SermonWatch.objects.filter(
                            user=request_user,
                            sermon=OuterRef("pk"),
                        )
                    ),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
            is_bookmarked=Case(
                When(
                    Exists(
                        SermonBookmark.objects.filter(
                            user=request_user,
                            sermon=OuterRef("pk"),
                        )
                    ),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
        )

        return queryset

    @action(methods=["POST"], detail=True, serializer_class=SermonWatchSerializer)
    def watch(self, request, *args, **kwargs):
        sermon = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={
                "sermon": sermon,
                "request": request,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, serializer_class=SermonBookmarkSerializer)
    def bookmark(self, request, *args, **kwargs):
        sermon = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={
                "sermon": sermon,
                "request": request,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
