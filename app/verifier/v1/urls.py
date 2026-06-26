from django.urls import path

from app.verifier.v1.views import EmailVerificationSendView, VerifierPhoneConfirmView, VerifierPhoneView

urlpatterns = [
    path("verifier/email/", EmailVerificationSendView.as_view()),
    path("verifier/phone/", VerifierPhoneView.as_view(), name="휴대폰 인증"),
    path("verifier/phone/confirm/", VerifierPhoneConfirmView.as_view(), name="휴대폰 인증 확인"),
]
