from django.db import models

from app.common.models import BaseModel


class Bible(BaseModel):
    data = models.FileField(verbose_name="데이터", upload_to="bible/")

    class Meta:
        db_table = "bible"
        verbose_name = "성경"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "성경"
