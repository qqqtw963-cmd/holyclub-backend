from datetime import datetime, timedelta
import logging

import jwt
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from jwt import ExpiredSignatureError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from app.bible_reading_log.models import BibleReadingLog
from app.common.validators import validate_serializer_request_user
from app.daily_check_status.models import DailyCheckStatus
from app.mortification_of_sin.models import MortificationOfSin
from app.pray_time_log.models import PrayTimeLog
from app.spiritual_discipline.models import SpiritualDiscipline
from app.user.models import ResidenceType, SocialKind, User, UserPushSettings
from app.user.social_adapters import SocialAdapter
from app.user.v1.nested_serializers import DeviceSerializer, UserPushSettingsReadSerializer
from app.user.validators import validate_phone_number_length
from app.verifier.models import EmailVerifier, PhoneVerifier

logger = logging.getLogger("request")


class UserSerializer(serializers.ModelSerializer):
    """
    http method: PUT, GET

    : 유저의 "추가 정보"를 "수정"합니다.
    - 이름/핸드폰번호: 수정 불가능
    - 국적은 유저가 지역시간 재설정 할 때
        >> 유저는 알지 못하지만 db저장할 때는 '지역시간'기준으로 국내/국외 구분해서 저장

    조회 시에만 UserPushSettings 정보도 함께 반환
    """

    user_push_settings = UserPushSettingsReadSerializer(
        source="push_user_settings",
        read_only=True,
    )
    weekly_faith_score = serializers.SerializerMethodField(
        read_only=True,
        help_text="주간 신앙 점수",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "residence",
            "name",
            "phone",
            "gender",
            "birth_date",
            "postal_code",
            "address",
            "address_detail",
            "church_name",
            "weekly_faith_score",
            "user_push_settings",
        ]
        read_only_fields = [
            "name",
            "phone",
            "weekly_faith_score",
            "user_push_settings",
        ]

    def _calculate_range_score(self, value, ranges):
        """범위별 점수 계산 헬퍼 메서드"""
        for threshold, score in ranges:
            if value <= threshold:
                return score
        return 0

    @extend_schema_field(serializers.IntegerField())
    def get_weekly_faith_score(self, obj):
        request_user = obj
        request = self.context.get("request")
        local_datetime_str = request.query_params.get("local_datetime") if request else None

        if not local_datetime_str:
            return 0

        try:
            # local_datetime 파싱
            target_date = datetime.strptime(local_datetime_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # ISO 형식도 시도
                target_date = datetime.fromisoformat(local_datetime_str.replace("Z", "+00:00")).date()
            except ValueError:
                return 0

        # 해당 날짜가 포함된 주의 시작일(일요일) 계산
        week_start_sunday = target_date - timedelta(days=(target_date.weekday() + 1) % 7)

        # 한 주의 날짜 (일요일부터 토요일까지)
        week_dates = [week_start_sunday + timedelta(days=i) for i in range(7)]

        # 1. 출석 점수 : 오늘의 체크(말씀, 기도, 예배, 산상수훈, 경건의 습관, 죄와의 싸움1,2) 중 하나라도 한 경우
        is_checked_daily = (
            BibleReadingLog.objects.filter(
                user=request_user,
                recognized_date=target_date,
            ).exists()
            or PrayTimeLog.objects.filter(
                user=request_user,
                recognized_date=target_date,
            ).exists()
            or DailyCheckStatus.objects.filter(
                user=request_user,
                recognized_date=target_date,
            ).exists()
            or SpiritualDiscipline.objects.filter(
                weekly_sd__user=request_user,
                recognized_date=target_date,
            ).exists()
            or MortificationOfSin.objects.filter(
                weekly_mos__user=request_user,
                recognized_date=target_date,
            ).exists()
        )

        # 2. 말씀: 한 주 동안 총 읽은 장 수
        total_bible_count = BibleReadingLog.objects.filter(
            user=request_user,
            recognized_date__in=week_dates,
        ).count()

        # 3. 기도: 한 주 동안 총 분(min)
        pray_logs = PrayTimeLog.objects.filter(
            user=request_user,
            recognized_date__in=week_dates,
        )
        total_pray_seconds = sum(log.duration_seconds for log in pray_logs)
        total_pray_minutes = total_pray_seconds // 60

        # 4. 죄와의 싸움 : 한 주 동안 한 번이라도 check한 경우
        is_checked_mos = MortificationOfSin.objects.filter(
            weekly_mos__user=request_user,
            recognized_date__in=week_dates,
        ).exists()

        # (총) 점수 로직 계산
        total_score = 0
        # 1. 출석점수
        if is_checked_daily:
            total_score += 10
        # 2&3. 말씀 및 기도 점수 계산
        total_score += self._calculate_range_score(
            total_bible_count,
            [
                (5, 6),  # 0~5 이면 6점 추가
                (10, 12),  # 6~10 이면 12점 추가
                (20, 18),  # 11~20 이면 18점 추가
                (30, 24),  # 21~30 이면 24점 추가
                (float("inf"), 30),  # 31 이상이면 30점 추가
            ],
        )
        total_score += self._calculate_range_score(
            total_pray_minutes,
            [
                (30, 6),  # 0~30 이면 6점 추가
                (60, 12),  # 31~60 이면 12점 추가
                (120, 18),  # 61~120 이면 18점 추가
                (180, 24),  # 121~180 이면 24점 추가
                (float("inf"), 30),  # 181 이상 이면 30점 추가
            ],
        )
        # 4. 죄와의 싸움
        if is_checked_mos:
            total_score += 15

        return int(total_score)

    def to_representation(self, instance):
        """조회 시에만 user_push_settings 포함"""
        data = super().to_representation(instance)

        # 수정 요청이 아닌 경우(조회)에만 user_push_settings 포함
        if self.context.get("request") and self.context["request"].method == "GET":
            return data
        else:
            # 수정 시에는 user_push_settings 제외
            data.pop("user_push_settings", None)
            return data


class UserEmailAuthSerializer(serializers.Serializer):
    """
    authentication I: email
    ---
    EmailVerificationSendSerializer 통해서 발송된 메일에 대해서
    회원가입/로그인 해주는 api
    """

    # request
    email = serializers.EmailField(write_only=True, required=False)
    code = serializers.CharField(write_only=True)

    device = DeviceSerializer(
        required=False,
        write_only=True,
        allow_null=True,
        help_text="이전에 회원가입 했고, 새로운 device로 로그인한 경우를 위해 입력받음",
    )

    # response
    is_register = serializers.BooleanField(read_only=True, label="인가 여부")
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):  # 로그인 로직
        email = attrs.get("email")
        code = attrs.pop("code")

        # ---- 테스트 계정용 우회 로직 ----
        if email == "test@test.com" and code == "000000":
            try:
                attrs["user"] = User.objects.get(email=email)
                attrs["is_register"] = True
            except User.DoesNotExist:
                attrs["is_register"] = False
            return attrs
        # ---- 앱 심사 이후 해당 코드 삭제 ----

        # 1. 이메일 유효성 검증
        try:
            email_verifier = EmailVerifier.objects.get(email=email, code=code)
        except EmailVerifier.DoesNotExist:
            raise ValidationError(
                {
                    "nonField": ["인증번호가 일치하지 않습니다."],
                    "errorCode": ["INVALID_VERIFICATION_CODE"],
                }
            )  # db에 없는 경우

        # 2. 최신 코드만 유효 검증 (보안 강화)
        latest_verifier = (
            EmailVerifier.objects.filter(
                email=email,
            )
            .order_by("-created_at")
            .first()
        )
        if not latest_verifier or latest_verifier.code != code:
            raise ValidationError(
                {
                    "nonField": ["유효하지 않은 인증번호입니다."],
                    "errorCode": ["INVALID_VERIFICATION_CODE"],
                }
            )

        # 3. 시간 만료 검증 (1시간)
        if email_verifier.created_at <= timezone.now() - timedelta(hours=1):
            raise ValidationError(
                {
                    "nonField": ["인증 가능 시간이 지났어요."],
                    "errorCode": ["VERIFICATION_CODE_EXPIRED"],
                }
            )

        # 4. 유저 존재 여부 검증
        try:
            attrs["user"] = User.objects.get(email=email)
            attrs["is_register"] = True
        except User.DoesNotExist:
            attrs["is_register"] = False
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        is_register = validated_data.get("is_register", False)
        if is_register:
            # 이미 유저 존재
            user = validated_data["user"]
            refresh = RefreshToken.for_user(user)

            # device 정보 업데이트
            if validated_data.get("device"):
                user.connect_device(**validated_data["device"])

            return {
                "is_register": True,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }
        else:
            # 회원가입으로 넘어감 (token필요)
            email_verifier = (
                EmailVerifier.objects.filter(
                    email=validated_data["email"],
                )
                .order_by("-created_at")
                .first()
            )
            return {
                "is_register": False,
                "access_token": email_verifier.token,
                "refresh_token": None,
            }


class UserSocialAuthSerializer(serializers.Serializer):
    """
    authentication II
    (response: token)
    """

    # request
    code = serializers.CharField(required=False, write_only=True, label="애플/카카오 모두 사용")
    state = serializers.ChoiceField(write_only=True, choices=SocialKind.choices)
    oauth_access_token = serializers.CharField(required=False, write_only=True, allow_null=True, label="카카오 access token 또는 Apple/Google id token")

    device = DeviceSerializer(
        required=False,
        write_only=True,
        allow_null=True,
        help_text="이전에 회원가입 했고, 새로운 device로 로그인한 경우를 위해 입력받음",
    )

    # response
    is_register = serializers.BooleanField(read_only=True)

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        state = attrs["state"]
        oauth_access_token = attrs.get("oauth_access_token")
        trace_id = self.context["request"].META.get("HTTP_X_TRACE_ID") or getattr(self.context["request"], "trace_id", "no-trace")

        logger.info("social_auth validate start trace=%s state=%s has_oauth_token=%s", trace_id, state, bool(oauth_access_token))

        if oauth_access_token:
            code = None
        else:
            code = attrs.get("code")

        logger.info("social_auth before get_social_user_id trace=%s state=%s", trace_id, state)
        social_user_id = self.get_social_user_id(code, oauth_access_token, state)
        logger.info("social_auth after get_social_user_id trace=%s state=%s social_user_id=%s", trace_id, state, social_user_id)
        social_email = f"{social_user_id}@{state}.social"

        try:
            attrs["user"] = User.objects.get(email=social_email)
            attrs["is_register"] = True
            logger.info("social_auth existing_user trace=%s state=%s email=%s", trace_id, state, social_email)
        except User.DoesNotExist:
            attrs["oauth_access_token"] = jwt.encode(
                payload={
                    "social_email": social_email,
                    "expired_at": timezone.now().timestamp() + 10 * 60,  # 10분간 유효함
                },
                key=settings.SECRET_KEY,
            )
            attrs["is_register"] = False
            logger.info("social_auth new_user trace=%s state=%s email=%s", trace_id, state, social_email)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        trace_id = self.context["request"].META.get("HTTP_X_TRACE_ID") or getattr(self.context["request"], "trace_id", "no-trace")
        is_register = validated_data.pop("is_register")
        logger.info("social_auth create start trace=%s is_register=%s has_device=%s", trace_id, is_register, bool(validated_data.get("device")))

        if not is_register:
            validated_data["access_token"] = validated_data.pop("oauth_access_token", None)
            validated_data["refresh_token"] = None
            logger.info("social_auth create return_signup_token trace=%s", trace_id)
            return validated_data

        user = validated_data["user"]
        logger.info("social_auth before jwt trace=%s user_id=%s", trace_id, user.id)
        refresh = user.get_token()
        logger.info("social_auth after jwt trace=%s user_id=%s", trace_id, user.id)
        validated_data["access_token"] = refresh.access_token
        validated_data["refresh_token"] = refresh

        if validated_data.get("device"):
            logger.info("social_auth before connect_device trace=%s user_id=%s", trace_id, user.id)
            user.connect_device(**validated_data["device"])
            logger.info("social_auth after connect_device trace=%s user_id=%s", trace_id, user.id)

        logger.info("social_auth create done trace=%s user_id=%s", trace_id, user.id)
        return validated_data

    def get_social_user_id(self, code, oauth_access_token, state):
        for adapter_class in SocialAdapter.__subclasses__():
            if adapter_class.key == state:
                origin = self.context["request"].META.get("HTTP_ORIGIN", "")
                return adapter_class(code, oauth_access_token, origin).get_social_user_id()
        raise ModuleNotFoundError(f"{state.capitalize()}Adapter class")


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    authorization
    : 최초의 유저 정보 입력 받기
    : request(token) 통해서 유저 객체를 생성
    : response( access_token, refresh_token) 알려주기
    : 이때 device 도 같이 받음
    """

    # request
    email = serializers.EmailField(
        required=False,
        help_text="소셜일 때는 X, 이메일 회원가입 시에만 입력",
    )
    auth_token = serializers.CharField(
        write_only=True,
        help_text="(소셜/이메일)인가된 토큰",
    )

    phone_token = serializers.CharField(
        write_only=True,
        required=False,
        help_text="residence가 국내이면 필수값, 국외이면 null",
    )

    device = DeviceSerializer(
        required=False,
        write_only=True,
        allow_null=True,
        help_text="회원가입 시, device 정보",
    )

    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    # response
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "social_kind",
            # auth
            "auth_token",  # email_token or social_token
            "email",
            "device",
            # info
            "residence",
            "name",
            "phone",
            "phone_token",  # wildcard: 123456789
            "gender",
            "birth_date",
            "postal_code",
            "address",
            "address_detail",
            "church_name",
            "local_datetime",  # request 용
            "access_token",
            "refresh_token",
        ]
        read_only_fields = [
            "access_token",
            "refresh_token",
        ]

    def validate(self, attrs):
        # 여기에서 residence가 overseas일때는 phone_token의 값이 없어도 괜찮도록 해줘

        # todo: Phone이 동일하면 동일한 유저로 판단하여, 로그인 불가능 하도록 validation > 기획적으로 그렇게 해도 되는지 문의 (일단 이렇게 하고, 만약 예외가 생기면 관리자 페이지에서 직접 유저 삭제 하는 것으로 )
        social_kind = attrs.get("social_kind", None)
        auth_token = attrs.pop("auth_token", None)

        phone = attrs.get("phone", None)
        phone_token = attrs.get("phone_token", None)  # pop 아니고 get 맞음

        # [email]
        if social_kind:
            # 소셜 회원가입
            try:
                payload = jwt.decode(
                    auth_token,
                    key=settings.SECRET_KEY,
                    algorithms=settings.SIMPLE_JWT_ALGORITHM,
                )
            except ExpiredSignatureError:
                raise ValidationError({"social_token": ["소셜로그인 토큰이 만료됐습니다."]})

            social_email = payload.pop("social_email", None)

            attrs["social_kind"] = social_email.split("@")[1].split(".")[0]
            attrs["email"] = social_email
        else:
            # 이메일 회원가입
            email = attrs["email"]
            # 이메일 토큰 검증
            try:
                EmailVerifier.objects.get(email=email, token=auth_token)
            except EmailVerifier.DoesNotExist:
                raise ValidationError({"email": ["이메일 인증을 진행해 주세요."]})

            # 이메일 검증
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    {
                        "nonField": ["이미 가입된 이메일이에요."],
                        "errorCode": ["ALREADY_EXISTING_EMAIL"],
                    }
                )

        # [소셜/이메일 공통]
        # (국내인 경우) phone 검증
        residence = attrs.get("residence")
        if residence == ResidenceType.DOMESTIC:
            validate_phone_number_length(phone)  # phone 길이 검증
            if not phone_token:
                # 휴대폰 토큰이 없는 경우
                raise ValidationError({"phone_token": ["이 필드는 필수 항목입니다."]})
            # wildcard
            if phone_token != "123456789":
                # 휴대폰 토큰 검증
                try:
                    self.phone_verifier = PhoneVerifier.objects.get(phone=phone, token=phone_token)
                except PhoneVerifier.DoesNotExist:
                    raise ValidationError(
                        {
                            "nonField": ["휴대폰 인증을 진행해 주세요."],
                            "errorCode": ["VERIFY_PHONE_NUMBER"],
                        }
                    )

        # [local_device_time -> offset / for push_setting]
        local_datetime = attrs.pop("local_datetime", None)
        if local_datetime and local_datetime.tzinfo:
            utc_offset = local_datetime.utcoffset()
            if utc_offset:
                attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data.get("phone")
        phone_token = validated_data.pop("phone_token", None)
        residence = validated_data.get("residence")

        # (국내인 경우) phone_verifier 처리
        if residence == ResidenceType.DOMESTIC:
            # wildcard
            if phone_token != "123456789":
                self.phone_verifier.delete()
            # DB 정리
            phone_verifier_set = PhoneVerifier.objects.filter(phone=phone)
            if phone_verifier_set.exists():
                phone_verifier_set.delete()

        device_data = validated_data.pop("device", None)
        timezone_offset = validated_data.pop("timezone_offset", 0)

        user = User.objects.create_user(**validated_data)

        UserPushSettings.objects.create(
            user=user,
            timezone_offset=timezone_offset,
        )

        refresh = RefreshToken.for_user(user)  # authentication

        # device 연결하기
        if device_data:
            user.connect_device(**device_data)

        user.access_token = str(refresh.access_token)
        user.refresh_token = str(refresh)

        return user


class UserPushSettingsSerializer(serializers.ModelSerializer):
    alarm_local_time = serializers.TimeField(
        write_only=True,
        required=False,
        allow_null=True,
        label="디바이스 기반 알림 받고 싶은 시간 (HH:MM:SS 형식)",
    )

    reset_local_datetime = serializers.DateTimeField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="재설정 사용자 디바이스의 현재 시간 (ISO8601 형식)",
    )  # 이걸 기반으로 timezone_offset 만 변경해주면 됨

    class Meta:
        model = UserPushSettings
        fields = [
            "id",
            "is_weekly_summary_alarm_enabled",
            # request
            "alarm_local_time",
            "reset_local_datetime",
            # response
            "alarm_time",
            "timezone_offset",
        ]
        read_only_fields = [
            "alarm_time",
            "timezone_offset",
        ]

    def validate(self, attrs):
        request_user = validate_serializer_request_user(self, attrs)

        try:
            user_push_settings = UserPushSettings.objects.get(user=request_user)
        except UserPushSettings.DoesNotExist:
            raise ValidationError({"default": ["존재하지 않는 객체입니다."]})

        # alarm_local_time 처리
        alarm_local_time = attrs.pop("alarm_local_time", None)
        if alarm_local_time:
            # 기존 timezone_offset을 이용해 UTC 시간으로 변환
            current_offset_minutes = user_push_settings.timezone_offset
            # 로컬 시간에 UTC로 변환
            today = datetime.today().date()
            local_datetime = datetime.combine(today, alarm_local_time)
            utc_datetime = local_datetime - timedelta(minutes=current_offset_minutes)
            attrs["alarm_time"] = utc_datetime.time()

        # reset_local_datetime 처리
        reset_local_datetime = attrs.pop("reset_local_datetime", None)
        if reset_local_datetime:
            if reset_local_datetime.tzinfo is None:
                raise ValidationError(
                    {
                        "reset_local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요."],
                    }
                )

            # timezone offset만 업데이트 (alarm_time은 건드리지 않음)
            utc_offset = reset_local_datetime.utcoffset()
            if utc_offset:
                attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60)

        attrs["user_push_settings"] = user_push_settings
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_push_settings = validated_data.pop("user_push_settings")  # 값이 늘 존재

        for attr, value in validated_data.items():
            setattr(user_push_settings, attr, value)
        user_push_settings.save()

        return user_push_settings


class UserLogoutSerializer(serializers.Serializer):
    uid = serializers.CharField(required=False, help_text="기기의 고유id")

    def create(self, validated_data):
        user = self.context["request"].user
        if validated_data.get("uid"):
            user.disconnect_device(validated_data["uid"])
        return {}


class UserRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh_token"])

        data = {"access_token": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh_token"] = str(refresh)

        return data
