from rest_framework.generics import CreateAPIView

from app.verifier.v1.serializers import (
    EmailVerificationSendSerializer,
    VerifierPhoneConfirmSerializer,
    VerifierPhoneSerializer,
)


class EmailVerificationSendView(CreateAPIView):
    """
    이메일 검증 메일 발송
    ---
    email_verification
    """

    serializer_class = EmailVerificationSendSerializer


# -----------------


class VerifierPhoneView(CreateAPIView):
    """
    휴대폰 인증
    ---
    """

    serializer_class = VerifierPhoneSerializer


class VerifierPhoneConfirmView(CreateAPIView):
    """
    휴대폰 인증 확인
    ---
    항상 허용되는 인증코드 : 000000
    """

    serializer_class = VerifierPhoneConfirmSerializer
