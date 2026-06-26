from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.websocket_connection.models import WebsocketConnection
from app.websocket_connection.v1.permissions import WebsocketConnectionPermission
from app.websocket_connection.v1.serializers import WebsocketConnectionSerializer, WebsocketDisconnectionSerializer


@extend_schema_view(
    connect=extend_schema(summary="WebsocketConnection 등록", exclude=True),
    disconnect=extend_schema(summary="WebsocketConnection 삭제", exclude=True),
)
class WebsocketConnectionViewSet(
    GenericViewSet,
):
    queryset = WebsocketConnection.objects.all()
    serializer_class = WebsocketConnectionSerializer
    permission_classes = [WebsocketConnectionPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    @action(methods=["POST"], detail=False, serializer_class=WebsocketConnectionSerializer)
    def connect(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={
                "id": request.data["id"],
                "access_token": request.data["query_params"].get("access_token"),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False, serializer_class=WebsocketDisconnectionSerializer)
    def disconnect(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
