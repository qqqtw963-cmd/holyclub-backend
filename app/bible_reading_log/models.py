from django.db import models

from app.common.models import BaseModel


class BibleReadingLog(models.Model):
    """데일리 입니다."""

    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
    )

    count = models.IntegerField(default=1)

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
        verbose_name="사용자 타임존 기준, 실제 날짜",
        db_index=True,
    )
    recognized_date = models.DateField(
        verbose_name="통계에서 사용되는 날짜",
        db_index=True,
        help_text="04:00 기준, 인정되는 날짜",
    )

    class Meta:
        db_table = "bible_reading_log"
        verbose_name = "성경 읽기 기록"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "recognized_date",
                ],
                name="unique_user_bible_reading_log",
            )
        ]
