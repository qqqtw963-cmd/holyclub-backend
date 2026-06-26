from ckeditor.fields import RichTextField
from django.db import models

from app.common.models import BaseModel


class TermsOfService(BaseModel):
    version = models.IntegerField(editable=False)
    content = RichTextField(
        config_name="legal",
        verbose_name="내용",
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            last_version = TermsOfService.objects.aggregate(max_version=models.Max("version"))["max_version"]
            self.version = (last_version or 0) + 1
        super().save(*args, **kwargs)

    class Meta:
        db_table = "terms_of_service"
        verbose_name = "이용약관"
        verbose_name_plural = "1. 서비스 이용약관"
        ordering = ["-version"]
