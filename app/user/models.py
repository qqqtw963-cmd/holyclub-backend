from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.validators import MinLengthValidator, validate_integer
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from app.common.models import BaseModel, BaseModelMixin
from app.device.models import Device


class UserManager(DjangoUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class BaseUser(BaseModelMixin, AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(
        verbose_name="이메일",
        unique=True,
    )
    # (phone: 아래 User에 존재함)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    is_staff = models.BooleanField(verbose_name="스태프", default=False)
    is_superuser = models.BooleanField(verbose_name="슈퍼유저여부", default=False)
    is_active = models.BooleanField(verbose_name="활성화여부", default=True)
    date_joined = models.DateTimeField(verbose_name="가입일", default=timezone.now)

    objects = UserManager()

    class Meta:
        abstract = True


class GenderType(models.TextChoices):
    MALE = "male", "남성"
    FEMALE = "female", "여성"


class ResidenceType(models.TextChoices):
    DOMESTIC = "domestic", "국내"
    OVERSEAS = "overseas", "국외"


class SocialKind(models.TextChoices):
    KAKAO = "kakao", "카카오"
    APPLE = "apple", "애플"
    # GOOGLE = "google", "구글"


class User(BaseUser):
    social_kind = models.CharField(
        verbose_name="소셜로그인 종류",
        max_length=8,
        choices=SocialKind.choices,
        null=True,
        blank=True,
    )

    # 이름/휴대폰번호/성별(enum)/생년월일(숫자만)/거주지/우편번호/주소/상세주소/출석교회
    residence = models.CharField(
        verbose_name="거주지",
        max_length=10,
        choices=ResidenceType.choices,
        blank=True,
        default="",
    )

    name = models.CharField(
        verbose_name="이름",
        max_length=50,
        help_text="최초 생성(설정) 이후 변경 불가능, 변경하고 싶다면 관리자페이지에서 직접 제어",
    )
    phone = models.CharField(
        verbose_name="휴대폰",
        max_length=11,
        blank=True,
        default="",
        validators=[validate_integer, MinLengthValidator(10)],
        help_text="최초 생성(설정) 이후 변경 불가능, 변경하고 싶다면 관리자페이지에서 직접 제어",
    )
    gender = models.CharField(verbose_name="성별", max_length=10, choices=GenderType.choices, default=GenderType.MALE)
    birth_date = models.CharField(
        verbose_name="생년월일",
        max_length=8,
        validators=[validate_integer, MinLengthValidator(8)],
        help_text="YYYYMMDD 형식",
    )
    postal_code = models.CharField(verbose_name="우편번호", max_length=20, blank=True, default="")  # 한국은 5글자, 해외는 20글자
    address = models.CharField(verbose_name="주소", max_length=200, blank=True, default="")
    address_detail = models.CharField(verbose_name="상세주소", max_length=200, blank=True, default="")
    church_name = models.CharField(verbose_name="출석교회", max_length=100, blank=True, default="")

    class Meta:
        db_table = "user"
        verbose_name = "유저"
        verbose_name_plural = "1. 회원"

    def get_token(self):
        return RefreshToken.for_user(self)

    def connect_device(self, uid, token):
        Device.objects.update_or_create(uid=uid, defaults={"user": self, "token": token})

    def disconnect_device(self, uid):
        self.device_set.filter(uid=uid).delete()


class UserPushSettings(BaseModel):
    user = models.OneToOneField(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name="유저",
        related_name="push_user_settings",
    )

    is_weekly_summary_alarm_enabled = models.BooleanField(
        verbose_name="통계 알림 여부",
        default=False,
    )
    alarm_time = models.TimeField(
        verbose_name="오늘의 체크 알림 시간 (UTC)",
        null=True,
        blank=True,
    )  # 스케줄러에서는 해당 값을 기준으로 보내주면 됨

    timezone_offset = models.IntegerField(
        verbose_name="분단위",
        default=0,
        help_text="디바이스와 UTC간의 차이(reset할 때 해당 값만 변경)",
    )

    class Meta:
        db_table = "user_push_setting"
        verbose_name = "유저별 푸시 설정"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.name}({self.user.pk}) | {self.alarm_time}-{self.timezone_offset}"
