from django.db import models

from app.common.models import BaseModel
from app.user.models import User


class Inquiry(BaseModel):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
    )  # 유저 삭제되면 여기 값은 Null 처리 되고, admin에는 탈퇴한 유저라고 나옴

    # 문의 작성 시점의 사용자 정보 저장 (탈퇴 후에도 유지)
    user_name = models.CharField(verbose_name="작성자 이름", max_length=50, null=True, blank=True)
    user_phone = models.CharField(verbose_name="작성자 휴대폰", max_length=11, null=True, blank=True)
    user_church_name = models.CharField(verbose_name="작성자 출석교회", max_length=100, null=True, blank=True)

    title = models.CharField(verbose_name="제목", max_length=128)
    content = models.TextField(verbose_name="내용")

    def save(self, *args, **kwargs):
        # 문의 생성 시 사용자 정보를 저장 (탈퇴 후에도 유지되도록)
        if not self.pk and self.user:  # 새로 생성되는 경우에만
            self.user_name = self.user.name
            self.user_phone = self.user.phone
            self.user_church_name = self.user.church_name
        super().save(*args, **kwargs)

    class Meta:
        db_table = "inquiry"
        verbose_name = "문의하기"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]


class InquiryProxy(Inquiry):
    class Meta:
        proxy = True
        app_label = "notification"
        verbose_name = "2. 문의 내역 확인"
        verbose_name_plural = verbose_name
