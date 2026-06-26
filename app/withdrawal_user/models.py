from django.core.validators import MinLengthValidator, validate_integer
from django.db import models

from app.common.models import BaseModel
from app.user.models import GenderType


class WithdrawalUser(models.Model):
    email = models.EmailField(
        verbose_name="이메일",
        help_text="탈퇴한 유저의 이메일",
    )

    # 필수 필드들 추가
    name = models.CharField(
        verbose_name="이름",
        max_length=50,
    )
    gender = models.CharField(verbose_name="성별", max_length=10, choices=GenderType.choices, default=GenderType.MALE)
    birth_date = models.CharField(
        verbose_name="생년월일",
        max_length=8,
        validators=[validate_integer, MinLengthValidator(8)],
        help_text="YYYYMMDD 형식",
    )
    phone = models.CharField(
        verbose_name="휴대폰",
        max_length=11,
        blank=True,
        default="",
        validators=[validate_integer, MinLengthValidator(10)],
        help_text="탈퇴 시점의 휴대폰 번호",
    )
    church_name = models.CharField(
        verbose_name="출석교회",
        max_length=100,
        blank=True,
        default="",
        help_text="탈퇴 시점의 출석교회",
    )

    # 사용자 생성 및 삭제 일시
    user_created_at = models.DateTimeField(
        verbose_name="사용자 계정 생성 일시",
        help_text="원래 User 객체가 생성된 일시",
    )
    deleted_at = models.DateTimeField(
        verbose_name="계정 삭제 일시",
        help_text="사용자가 탈퇴한 일시",
    )

    class Meta:
        db_table = "withdrawal_user"
        verbose_name = "탈퇴한 유저"
        verbose_name_plural = verbose_name
        ordering = ["-deleted_at"]


class WithdrawalUserProxy(WithdrawalUser):
    class Meta:
        proxy = True
        app_label = "user"
        verbose_name = "2. 탈퇴한 유저"
        verbose_name_plural = verbose_name
