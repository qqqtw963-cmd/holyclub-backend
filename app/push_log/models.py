import json
import logging
import math

from django.db import models
from firebase_admin import messaging
from firebase_admin.messaging import AndroidConfig, AndroidNotification

from app.common.models import BaseModel
from app.sms_log.models import SmsLog

logger = logging.getLogger(__name__)


class PushLogStatus(models.TextChoices):
    READY = "R", "대기"
    SUCCESS = "S", "성공"
    FAILURE = "F", "실패"


class PushLogType(models.TextChoices):
    STATISTICS_NOTIFICATION = "statistics_notification", "통계 알림"  # 매주 1번, 일요일 저녁 6시 (유저디바이스기반 시간)
    DAILY_CHECK_NOTIFICATION = "daily_check_notification", "오늘의 체크 알림"  # 매일 1번, 유저가 직접 설정한 시간


class PushLog(BaseModel):
    to_set = models.ManyToManyField("device.Device", verbose_name="수신자")
    type = models.CharField(verbose_name="푸시 알림 종류", max_length=25, choices=PushLogType.choices)
    title = models.CharField(verbose_name="제목", max_length=128)
    content = models.TextField(verbose_name="내용")
    navigation_data = models.JSONField(
        verbose_name="네비게이션 데이터",
        null=True,
        blank=True,
        help_text="앱에서 알림 클릭 시 이동할 화면 정보 (JSON 형태)",
    )
    status = models.CharField(
        verbose_name="상태", max_length=1, choices=PushLogStatus.choices, default=PushLogStatus.READY
    )
    fail_reason = models.TextField(verbose_name="실패사유", blank=True, default="")

    class Meta:
        db_table = "push_log"
        verbose_name = "푸시 로그"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.pk}. {self.title}"

    def send(self):
        logger.info(f"[DEBUG] PushLog {self.id} send() 메서드 시작")

        device_set = self.to_set.all()
        logger.info(f"[DEBUG] PushLog {self.id} - 대상 디바이스 수: {len(device_set)}")

        if not device_set:
            logger.warning(f"[DEBUG] PushLog {self.id} - 대상 디바이스가 없음!")
            self.status = PushLogStatus.FAILURE
            self.fail_reason = "대상 디바이스가 없음"
            self.save()
            return

        failed_device_set = []

        try:
            for i in range(math.ceil(len(device_set) / 500)):
                batch_devices = device_set[500 * i : 500 * (i + 1)]
                tokens = [device.token for device in batch_devices]

                logger.info(f"[DEBUG] PushLog {self.id} - 배치 {i+1} 발송 시작, 토큰 수: {len(tokens)}")
                for device in batch_devices:
                    logger.info(f"[DEBUG] 디바이스 토큰: {device.token[:20]}...")

                message = messaging.MulticastMessage(
                    tokens=tokens,
                    notification=messaging.Notification(
                        title=self.title,
                        body=self.content,
                    ),
                    data=self.navigation_data,
                    android=AndroidConfig(
                        priority="high",
                        notification=AndroidNotification(
                            channel_id="default",
                        ),
                    ),
                )

                logger.info(f"[DEBUG] PushLog {self.id} - Firebase 메시지 전송 중...")

                fail_reasons = []
                response = messaging.send_each_for_multicast(message)

                logger.info(
                    f"[DEBUG] PushLog {self.id} - FCM 응답: 성공={response.success_count}, 실패={response.failure_count}"
                )

                if response.failure_count > 0:
                    # FCM 응답의 실패
                    responses = response.responses
                    for idx, resp in enumerate(responses):
                        if not resp.success:
                            failed_device_set.append(batch_devices[idx])
                            error_msg = f"토큰: {tokens[idx][:20]}..., 에러: {resp.exception}"
                            fail_reasons.append(error_msg)
                            logger.error(f"[DEBUG] PushLog {self.id} - {error_msg}")

                    self.status = PushLogStatus.FAILURE
                    self.fail_reason = json.dumps(fail_reasons[:10])
                else:
                    self.status = PushLogStatus.SUCCESS
                    logger.info(f"[DEBUG] PushLog {self.id} - 모든 메시지 성공!")

        except Exception as e:
            logger.error(f"[DEBUG] PushLog {self.id} - Firebase 전송 중 예외: {str(e)}")
            import traceback

            logger.error(f"[DEBUG] 상세 에러: {traceback.format_exc()}")
            self.status = PushLogStatus.FAILURE
            self.fail_reason = f"Firebase 전송 예외: {str(e)}"

        self.save()
        logger.info(f"[DEBUG] PushLog {self.id} - 최종 상태: {self.status}")

        if failed_device_set:
            logger.info(f"[DEBUG] PushLog {self.id} - 실패한 디바이스 {len(failed_device_set)}개 삭제")
            self.to_set.model.objects.filter(id__in=[device.id for device in failed_device_set]).delete()


class PushLogProxy(PushLog):
    class Meta:
        proxy = True
        app_label = "email_log"
        verbose_name = "3. 푸시알림 발송 내역"
        verbose_name_plural = verbose_name
