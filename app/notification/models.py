from ckeditor.fields import RichTextField
from django.db import models

from app.common.models import BaseModel


class Notification(BaseModel):
    title = models.CharField(
        verbose_name="제목",
        max_length=24,
        help_text="제목은 최대 24자입니다.",
    )
    content = RichTextField(
        config_name="legal",
        verbose_name="내용",
    )

    class Meta:
        db_table = "notification"
        verbose_name = "공지사항"
        verbose_name_plural = "1. 공지사항 등록"
        ordering = ["-created_at"]
