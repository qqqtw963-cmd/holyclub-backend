import hashlib
import hmac
import platform
import uuid

import requests
from django.conf import settings
from django.db import models
from django.utils import timezone

from app.common.models import BaseModel


class SmsLogStatus(models.TextChoices):
    READY = "R", "대기"
    SUCCESS = "S", "성공"
    FAILURE = "F", "실패"


class SmsLog(BaseModel):
    to_set = models.JSONField(verbose_name="수신자", default=list)
    title = models.CharField(verbose_name="제목", max_length=128)
    content = models.TextField(verbose_name="내용")
    status = models.CharField(verbose_name="상태", max_length=1, choices=SmsLogStatus.choices, default=SmsLogStatus.READY)
    fail_reason = models.TextField(verbose_name="실패사유", blank=True, default="")

    class Meta:
        db_table = "sms_log"
        verbose_name = "문자 로그"
        verbose_name_plural = verbose_name

    def send(self):
        date = timezone.now().isoformat()
        salt = str(uuid.uuid1().hex)
        combined_string = date + salt

        headers = {
            "Authorization": "HMAC-SHA256 ApiKey="
            + settings.COOLSMS_API_KEY
            + ", Date="
            + date
            + ", salt="
            + salt
            + ", signature="
            + hmac.new(settings.COOLSMS_API_SECRET.encode(), combined_string.encode(), hashlib.sha256).hexdigest(),
            "Content-Type": "application/json; charset=utf-8",
        }
        data = {
            "agent": {
                "sdkVersion": "python/4.2.0",
                "osPlatform": platform.platform() + " | " + platform.python_version(),
            },
            "messages": [
                {
                    "from": settings.COOLSMS_FROM_PHONE,
                    "to": to,
                    "text": self.content,
                }
                for to in self.to_set
            ],
        }
        response = requests.request(
            method="post",
            url="https://api.coolsms.co.kr/messages/v4/send-many",
            headers=headers,
            json=data,
        )
        if response.ok:
            self.status = SmsLogStatus.SUCCESS
        else:
            self.status = SmsLogStatus.FAILURE
            self.fail_reason = f"HTTP {response.status_code}: {response.text}"
        self.save()


class SmsLogProxy(SmsLog):
    class Meta:
        proxy = True
        app_label = "email_log"
        verbose_name = "2. 문자 발송 내역"
        verbose_name_plural = verbose_name
