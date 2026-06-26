from ckeditor.fields import RichTextField
from django.db import models

from app.common.models import BaseModel


class PrivacyPolicy(BaseModel):
    version = models.IntegerField(editable=False)
    content = RichTextField(
        config_name="legal",
        verbose_name="내용",
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            last_version = PrivacyPolicy.objects.aggregate(max_version=models.Max("version"))["max_version"]
            self.version = (last_version or 0) + 1
        super().save(*args, **kwargs)

    class Meta:
        db_table = "privacy_policy"
        verbose_name = "개인정보처리방침"
        verbose_name_plural = verbose_name
        ordering = ["-version"]


class PrivacyPolicyProxy(PrivacyPolicy):
    class Meta:
        proxy = True
        app_label = "terms_of_service"
        verbose_name = "2. 개인정보 처리방침"
        verbose_name_plural = verbose_name
