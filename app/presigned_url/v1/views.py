from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from app.presigned_url.v1.serializers import PresignedSerializer


@extend_schema(
    summary="미리 서명된 URL 발급",
    description="""
![file_upload_flow](%sdocs/file_upload_flow.png)
* 플로우 1, 2를 input onChange 핸들러에서 실행해야합니다.
1. 미시 서명된 URL 발급
2. 미리 서명된 URL로 파일 업로드
    - method: `POST`
    - url: `url` (1에서 발급받은 url)
    - form-data: { ...fields, 'Content-Type': '{file.type}/' }
"""
    % settings.STATIC_URL,
)
class PresignedUrlCreateView(CreateAPIView):
    serializer_class = PresignedSerializer
    permission_classes = [IsAuthenticated]
