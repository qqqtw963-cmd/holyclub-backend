from django.db import models

from app.common.models import BaseModel
from app.user.models import User


class PrayerJournal(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    title = models.CharField(verbose_name="제목", max_length=128)
    content = models.TextField(verbose_name="내용")

    start_date = models.DateField(
        verbose_name="기도 시작 일자",
    )  # admin 상으로 입력받지 않음 / api 상으로 입력 (required=False) / 최초 저장 : created_at & 수정시: 직접 PUT으로

    is_answered = models.BooleanField(
        verbose_name="응답 여부",
        default=False,
    )
    answer_date = models.DateField(
        verbose_name="기도 응답 일자",
        null=True,
        blank=True,
    )  # 해당 변수에 대해서는 utc 기반으로 (4:00 기준 X)

    class Meta:
        db_table = "prayer_journal"
        verbose_name = "기도 제목"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
