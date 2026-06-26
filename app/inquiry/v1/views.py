from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.inquiry.models import Inquiry
from app.inquiry.v1.permissions import InquiryPermission
from app.inquiry.v1.serializers import InquirySerializer


@extend_schema_view(
    create=extend_schema(summary="문의하기 등록"),
)
class InquiryViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [InquiryPermission]
    pagination_class = None
    filterset_class = None

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset
