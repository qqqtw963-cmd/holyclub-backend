from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.terms_of_service.models import TermsOfService
from app.terms_of_service.v1.permissions import TermsOfServicePermission
from app.terms_of_service.v1.serializers import TermsOfServiceSerializer


class CurrentTermsOfServiceView(APIView):
    permission_classes = [TermsOfServicePermission]

    @extend_schema(
        summary="현재의 유효한 이용약관 조회",
        responses={200: TermsOfServiceSerializer},
    )
    def get(self, request):
        current_terms = TermsOfService.objects.order_by("-version").first()

        if current_terms is None:
            return Response({"error": "이용약관이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TermsOfServiceSerializer(current_terms)
        return Response(serializer.data)
