from django.db import models

from app.bible.utils import BibleBookType
from app.common.models import BaseModel


class BibleReadingStatus(BaseModel):
    """
    response로 내려줄 때, updated_at 기준 (+offset)으로 내려주기,
    """

    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    book = models.CharField(
        verbose_name="성경",
        max_length=20,
        choices=BibleBookType.choices,
    )
    chapter = models.PositiveIntegerField(verbose_name="장")

    timezone_offset = models.IntegerField(
        verbose_name="분단위",
        null=True,
        blank=True,
        help_text="디바이스와 UTC간의 차이",
    )

    count = models.IntegerField(
        verbose_name="해당 유저가 해당 책/장을 몇 번 읽었는지(날짜와 상관 없이)",
        default=1,
    )

    class Meta:
        db_table = "bible_reading_status"
        verbose_name = "성경 읽기 상태"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book", "chapter"],
                name="unique_user_bible_reading_status",
            )
        ]
