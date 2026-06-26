from django.db import models

from app.common.models import BaseModel


class WeeklySpiritualDiscipline(BaseModel):
    """
    user/week_start_sunday -> 1쌍만 존재
    """

    user = models.ForeignKey(
        "user.User",
        verbose_name="유저",
        on_delete=models.CASCADE,
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
        db_table = "weekly_spiritual_discipline"
        verbose_name = "(주간) 경건의 훈련"
        verbose_name_plural = "(주간) 경건의 습관"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "week_start_sunday"],
                name="unique_user_spiritual_discipline",
            )
        ]


class SpiritualDiscipline(BaseModel):
    weekly_sd = models.ForeignKey(
        "spiritual_discipline.WeeklySpiritualDiscipline",
        verbose_name="한 주의 내용 (경건의 훈련)",
        on_delete=models.CASCADE,
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
        db_table = "spiritual_discipline"
        verbose_name = "(데일리) 경건의 훈련"
        verbose_name_plural = "(데일리) 경건의 습관"  # check
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["weekly_sd", "recognized_date"],
                name="unique_weekly_sd_recognized_date",
            )
        ]
