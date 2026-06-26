from django.db import models

from app.common.models import BaseModel


class EmailLogStatus(models.TextChoices):
    READY = "R", "대기"
    SUCCESS = "S", "성공"
    FAILURE = "F", "실패"


class EmailSendPurposeChoices(models.TextChoices):
    EMAIL_AUTHENTICATION = "email_authentication", "이메일 인증"


class EmailLog(BaseModel):
    recipient = models.CharField(verbose_name="수신자", max_length=128, default="")
    purpose = models.CharField(verbose_name="목적", choices=EmailSendPurposeChoices.choices, max_length=128)
    status = models.CharField(
        verbose_name="상태", max_length=1, choices=EmailLogStatus.choices, default=EmailLogStatus.READY
    )
    fail_reason = models.TextField(verbose_name="실패사유", blank=True, default="")

    class Meta:
        db_table = "email_log"
        verbose_name = "이메일 로그"
        verbose_name_plural = "1. 이메일 발송 내역"
