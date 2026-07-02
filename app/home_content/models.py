from django.db import models

from app.common.models import BaseModel


class HomeContent(BaseModel):
    eyebrow = models.CharField(
        verbose_name="상단 꼬리표",
        max_length=80,
        default="하나님과 더 가까워지는 거룩한 습관",
    )
    main_title = models.CharField(
        verbose_name="메인 제목",
        max_length=120,
    )
    sub_title = models.TextField(
        verbose_name="서브 설명",
    )
    highlight_text = models.CharField(
        verbose_name="강조 문구",
        max_length=120,
        blank=True,
        default="",
    )
    cta_text = models.CharField(
        verbose_name="CTA 문구",
        max_length=80,
        blank=True,
        default="",
    )
    cta_link = models.URLField(
        verbose_name="CTA 링크",
        blank=True,
        default="",
    )
    is_active = models.BooleanField(
        verbose_name="활성화 여부",
        default=True,
    )

    class Meta:
        db_table = "home_content"
        verbose_name = "홈 콘텐츠"
        verbose_name_plural = verbose_name
        ordering = ["-is_active", "-updated_at", "-created_at"]

    def __str__(self):
        return self.main_title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            type(self).objects.exclude(pk=self.pk).filter(is_active=True).update(is_active=False)
