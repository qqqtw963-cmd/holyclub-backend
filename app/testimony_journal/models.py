from django.db import models

from app.common.models import BaseModel


class TestimonyJournal(BaseModel):
    """
    어드민에서 보여지지 않도록, 유저만 조회 가능하도록
    """

    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="내용")

    class Meta:
        db_table = "testimony_journal"
        verbose_name = "고백록"
        verbose_name_plural = "(admin에서 안 보여질 예정) 고백록"
        ordering = ["-created_at"]
