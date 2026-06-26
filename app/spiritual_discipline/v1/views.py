from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.spiritual_discipline.models import SpiritualDiscipline
from app.spiritual_discipline.v1.permissions import SpiritualDisciplinePermission
from app.spiritual_discipline.v1.serializers import SpiritualDisciplineSerializer, WeeklySpiritualDisciplineSerializer

# TODO [오늘의 체크] 페이지 안에 들어가는 전체 값 >> dashboard로 만들기


@extend_schema_view(
    # list=extend_schema(summary="(해당 주간) 경건의 습관 목록 조회"),
    create=extend_schema(summary="(오늘의) 경건의 습관 on/off"),
    weekly=extend_schema(summary="(해당 주간) 경건의 습관 등록", description="등록만 가능, 수정/삭제 불가능"),
)
class SpiritualDisciplineViewSet(
    # mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = SpiritualDiscipline.objects.all()
    serializer_class = SpiritualDisciplineSerializer
    permission_classes = [SpiritualDisciplinePermission]
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

    @action(methods=["POST"], detail=False, serializer_class=WeeklySpiritualDisciplineSerializer)
    def weekly(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
