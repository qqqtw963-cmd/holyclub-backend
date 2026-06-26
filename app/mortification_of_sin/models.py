from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from app.common.models import BaseModel


class WeeklyMortificationOfSinSlot(models.TextChoices):
    FIRST = "first", "죄와의 싸움 1"
    SECOND = "second", "죄와의 싸움 2"


class WeeklyMortificationOfSin(BaseModel):
    """
    user/slot/week_start_sunday -> 1쌍만 존재
    """

    user = models.ForeignKey(
        "user.User",
        verbose_name="유저",
        on_delete=models.CASCADE,
    )

    slot = models.CharField(
        verbose_name="순서",
        max_length=10,
        choices=WeeklyMortificationOfSinSlot.choices,
    )
    practice = models.CharField(
        verbose_name="내용",
        max_length=500,
    )
    week_start_sunday = models.DateField(
        verbose_name="주 시작일 (일요일)",
        help_text="해당 주의 일요일 날짜",
    )  # 생성일 기반으로, 객체 생성시, 해당 주 일요일 일자를 저장하도록

    class Meta:
        db_table = "weekly_mortification_of_sin"
        verbose_name = "(주간) 죄 죽이기"
        verbose_name_plural = "(주간) 죄와의 싸움"  # 점수
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "slot", "week_start_sunday"],
                name="unique_user_slot_week_mortification_of_sin",
            )
        ]

    # def get_average_score(self):
    #     """주간 평균 점수 계산 (실시간)"""
    #     scores = self.daily_mos_set.values_list("score", flat=True)
    #     if scores:
    #         return sum(scores) / len(scores)
    #     return 0


class MortificationOfSin(BaseModel):
    weekly_mos = models.ForeignKey(
        "mortification_of_sin.WeeklyMortificationOfSin",
        verbose_name="한 주의 내용 (죄와의 싸움)",
        on_delete=models.CASCADE,
        related_name="daily_mos_set",
    )

    score = models.PositiveSmallIntegerField(
        verbose_name="점수",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="0~10점 사이의 점수",
    )

    timezone_offset = models.IntegerField(
        verbose_name="분단위",
        null=True,
        blank=True,
        help_text="디바이스와 UTC간의 차이",
    )  # read_only

    local_date = models.DateField(
        verbose_name="사용자 타임존 기준, 실제 날짜",
        db_index=True,
    )  # read_only
    recognized_date = models.DateField(
        verbose_name="통계에서 사용되는 날짜",
        db_index=True,
        help_text="04:00 기준, 인정되는 날짜",
    )  # read_only

    class Meta:
        db_table = "mortification_of_sin"
        verbose_name = "(데일리) 죄 죽이기"
        verbose_name_plural = "(데일리) 죄와의 싸움"  # 점수
        ordering = ["-created_at"]
