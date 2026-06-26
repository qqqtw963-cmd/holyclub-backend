from django.db import models

from app.common.models import BaseModel


class PrayType(models.TextChoices):
    TIMER = "timer", "타이머"
    STOPWATCH = "stopwatch", "스톱워치"
    MANUAL = "manual", "수동입력"


class PrayTimeLog(models.Model):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
    )

    type = models.CharField(
        verbose_name="기록 방식",
        choices=PrayType.choices,
        max_length=20,
    )

    # 시간/시점
    created_at = models.DateTimeField(
        verbose_name="생성일시(읽은일시)",
        help_text="UTC 기준",
    )  # read_only
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

    # 스톱워치용
    started_time = models.TimeField(
        verbose_name="(스톱워치용)시작시간",
        null=True,
        blank=True,
        help_text="스톱워치일 때는 값을 넣어줍니다. 타이머/수동일 때는 null처리",
    )
    ended_time = models.TimeField(
        verbose_name="(스톱워치용)종료시간",
        null=True,
        blank=True,
        help_text="스톱워치일 때는 값을 넣어줍니다. 타이머/수동일 때는 null처리",
    )

    # 타이머/스톱워치/수동 (둘다)
    duration_seconds = models.PositiveIntegerField(
        verbose_name="기도 시간(초)",
        help_text="기도한 시간을 초 단위로 저장 (최대 86,400초)",
    )  # 타이머/수동: 그대로 저장 / 스톱워치: BE에서 직접 계산 후 저장

    # 시리얼라이저에서 안 받지만, 모델에 저장될 때는 무조건 값이 있도록

    class Meta:
        db_table = "pray_time_log"
        verbose_name = "기도 시간 기록"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
