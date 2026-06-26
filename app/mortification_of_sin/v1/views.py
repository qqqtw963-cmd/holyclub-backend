from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.mortification_of_sin.models import MortificationOfSin
from app.mortification_of_sin.v1.permissions import MortificationOfSinPermission
from app.mortification_of_sin.v1.serializers import MortificationOfSinSerializer, WeeklyMortificationOfSinSerializer


@extend_schema_view(
    # list=extend_schema(summary="(해당 주간) 목록 조회"),
    create=extend_schema(summary="(오늘의) 죄와의 싸움 점수 등록/재등록"),
    weekly=extend_schema(summary="(해당 주간) 죄와의 싸움 등록", description="등록만 가능, 수정/삭제 불가능"),
)
class MortificationOfSinViewSet(
    # mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = MortificationOfSin.objects.all()
    serializer_class = MortificationOfSinSerializer
    permission_classes = [MortificationOfSinPermission]
    pagination_class = None
    filterset_class = None

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # 삭제된 경우 (DeletedInstance 또는 None 반환)
        if instance is None or hasattr(instance, "deleted"):
            return Response({}, status=status.HTTP_200_OK)

        # 생성된 경우
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=["POST"], detail=False, serializer_class=WeeklyMortificationOfSinSerializer)
    def weekly(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
