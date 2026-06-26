from django.db import models

from app.bible.utils import BibleBookType
from app.common.models import BaseModel
from app.user.models import User


class BibleHighlightColorType(models.TextChoices):
    RED = "red", "빨강"
    YELLOW = "yellow", "노랑"
    GREEN = "green", "초록"
    BLUE = "blue", "파랑"
    PURPLE = "purple", "보라"


class BibleHighlight(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    book = models.CharField(
        verbose_name="성경",
        max_length=20,
        choices=BibleBookType.choices,
    )
    chapter = models.PositiveIntegerField(verbose_name="장")
    verse = models.PositiveIntegerField(verbose_name="절")
    color = models.CharField(
        verbose_name="색상",
        max_length=20,
        choices=BibleHighlightColorType.choices,
    )  # 색상을 바꿀 수 있음

    class Meta:
        db_table = "bible_highlight"
        verbose_name = "성경 하이라이트"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book", "chapter", "verse", "color"],
                name="unique_user_bible_highlight",
            )
        ]
