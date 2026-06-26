from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.privacy_policy.models import PrivacyPolicy
from app.privacy_policy.v1.permissions import PrivacyPolicyPermission
from app.privacy_policy.v1.serializers import PrivacyPolicySerializer


class CurrentPrivacyPolicyView(APIView):
    permission_classes = [PrivacyPolicyPermission]

    @extend_schema(
        summary="현재의 유효한 개인정보처리방침 조회",
        responses={200: PrivacyPolicySerializer},
    )
    def get(self, request):
        current_policy = PrivacyPolicy.objects.order_by("-version").first()

        if current_policy is None:
            return Response({"error": "개인정보처리방침이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PrivacyPolicySerializer(current_policy)
        return Response(serializer.data)
