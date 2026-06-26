import re
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.email_log.models import EmailSendPurposeChoices
from app.email_log.utils import send_email_with_django_template
from app.user.models import User
from app.verifier.models import EmailVerifier, PhoneVerifier
from app.verifier.v1.utils import generate_verification_code, generate_verification_token, send_sms_verification_code


class EmailVerificationSendSerializer(serializers.Serializer):
    """
    이메일 (존재 여부) 검증 후 메일 전송
    : 이메일로 회원가입하기
    : purpose 필드에 대해서 삭제함 무조건 이메일 검증밖에 없어서!
    """

    email = serializers.EmailField(required=True)

    class Meta:
        model = EmailVerifier
        fields = [
            "email",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        code = generate_verification_code()
        token = generate_verification_token(email, code)

        validated_data.update(
            {
                "code": code,
                "token": token,
                "created_at": timezone.now(),
            }
        )
        try:
            # TODO naver/google : 이메일 양식 깨지는거 확인하기
            send_email_with_django_template(
                recipient=email,
                title="[이긴자] 이메일 인증을 위한 인증번호 발송 메일입니다.",
                purpose=EmailSendPurposeChoices.EMAIL_AUTHENTICATION,  # 무조건 이거 하나밖에 없음
                context={
                    "code": code,
                },
            )
        except Exception as e:
            print("SES Send Error ", e)
            raise ValidationError({"email": [f"인증번호 전송 실패: {e}"]})

        EmailVerifier.objects.create(**validated_data)
        return validated_data


# -----------------


class VerifierPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerifier
        fields = ["phone"]

    def validate(self, attrs):
        phone = attrs["phone"]

        if not bool(re.match("01[0-9]{8,9}", phone)):
            raise ValidationError(
                {
                    "nonField": ["올바른 핸드폰 번호 형식이 아닙니다."],
                    "errorCode": ["INVALID_PHONE_NUMBER_FORMAT"],
                }
            )

        if User.objects.filter(phone=phone).exists():
            raise ValidationError({"phone": ["이미 가입된 번호에요"]})

        code = generate_verification_code()
        token = generate_verification_token(phone, code)

        attrs.update(
            {
                "code": code,
                "token": token,
                "created_at": timezone.now(),
            }
        )

        try:
            send_sms_verification_code(attrs["phone"], attrs["code"])
        except Exception:
            raise ValidationError({"phone": ["인증번호 전송 실패"]})

        return attrs


class VerifierPhoneConfirmSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = PhoneVerifier
        fields = [
            "phone",
            "code",
            "token",
        ]

    def validate(self, attrs):
        phone = attrs.pop("phone")
        code = attrs.pop("code")

        # wildcard
        if code == "000000":
            attrs.update({"token": "123456789"})
            return attrs

        try:
            phone_verifier = PhoneVerifier.objects.get(
                phone=phone,
                code=code,
            )
        except PhoneVerifier.DoesNotExist:
            raise ValidationError({"code": ["인증번호가 일치하지 않아요."]})

        # 1. 마지막 인증번호가 아닌 경우
        if code != PhoneVerifier.objects.filter(phone=phone).first().code:
            raise ValidationError({"code": ["최신 인증번호를 입력해 주세요."]})

        # 2. 3분이 지나서 만료된 경우
        if timezone.now() - phone_verifier.created_at > timedelta(minutes=3):
            raise ValidationError({"code": ["인증번호가 만료되었습니다."]})

        # 인증 성공 시 token 반환
        attrs.update({"token": phone_verifier.token})
        return attrs

    def create(self, validated_data):
        return validated_data
