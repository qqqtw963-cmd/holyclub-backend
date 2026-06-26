from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.serializers import PresignedSerializer


class PresignedMixin:
    # file_location = # model field upload to
    # file_limit_size = 20971520  # 20MB
    # file_extensions = []

    @extend_schema_view(summary="Presigned 생성")
    @action(methods=["POST"], detail=False, serializer_class=PresignedSerializer)
    def presigned(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
