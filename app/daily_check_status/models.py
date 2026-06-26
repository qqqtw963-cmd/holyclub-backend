from django.db import models

from app.common.models import BaseModel


class CheckType(models.TextChoices):
    SOM_READING_STATUS = "som_reading_status", "산상수훈"
    WORSHIP = "worship", "예배"


class DailyCheckStatus(models.Model):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
    )

    check_type = models.CharField(
        max_length=20,
        choices=CheckType.choices,
        verbose_name="체크 유형",
    )

    # 시간/시점
    created_at = models.DateTimeField(
        verbose_name="생성일시(읽은일시)",
        help_text="UTC 기준",
    )
    timezone_offset = models.IntegerField(
        verbose_name="분단위",
        null=True,
        blank=True,
        help_text="디바이스와 UTC간의 차이",
    )

    local_date = models.DateField(
        db_index=True,
        help_text="사용자 타임존 기준, 실제 날짜",
    )
    recognized_date = models.DateField(
        db_index=True,
        help_text="04:00 기준, 인정되는 날짜",
    )

    class Meta:
        db_table = "daily_check_status"
        verbose_name = "(예배/산상수훈) 매일 체크 상태"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
