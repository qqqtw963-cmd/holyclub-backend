from django.db import models

from app.common.models import BaseModel


class BibleVersion(BaseModel):
    bible = models.ForeignKey("bible.Bible", verbose_name="성경", on_delete=models.CASCADE, related_name="version_set")
    name = models.CharField(verbose_name="버전명", max_length=20, unique=True)

    class Meta:
        db_table = "bible_version"
        verbose_name = "성경 버전"
        verbose_name_plural = verbose_name
        ordering = ["name"]
