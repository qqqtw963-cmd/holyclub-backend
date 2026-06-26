import hashlib
import logging
import random

from django.utils import timezone

from app.sms_log.models import SmsLog, SmsLogStatus

logger = logging.getLogger(__name__)


def generate_verification_code():
    return str(random.randint(100000, 999999))


def generate_verification_token(obj, code):
    hash_string = f"{obj}{code}{timezone.now().timestamp()}"
    return hashlib.sha1(hash_string.encode("utf-8")).hexdigest()


def send_sms_verification_code(phone_number, verification_code):
    try:
        sms_log = SmsLog.objects.create(
            to_set=[phone_number],
            title="회원가입 인증번호",
            content=f"[이긴자(본인확인)] 인증번호는 [{verification_code}]입니다.",
            status=SmsLogStatus.READY,
        )
        sms_log.send()

        if sms_log.status == SmsLogStatus.FAILURE:
            raise Exception(f"SMS 전송 실패: {sms_log.fail_reason}")

        return sms_log
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}. Error: {e}")
        raise e
