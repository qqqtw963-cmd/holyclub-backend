import logging

from app.device.models import Device
from app.push_log.models import PushLog, PushLogStatus, PushLogType
from app.user.models import User

logger = logging.getLogger(__name__)

PUSH_LOG_MESSAGES = {
    PushLogType.STATISTICS_NOTIFICATION: {
        "title": "통계 알림",
        "content": "한 주의 체크리스트 통계 보기",
        "navigation_data": {"screen": "Statistics", "tab": "notification"},
    },
    PushLogType.DAILY_CHECK_NOTIFICATION: {
        "title": "오늘의 체크 알림",
        "content": "오늘의 체크리스트 작성하기",
        "navigation_data": {"screen": "DailyCheck", "tab": "notification"},
    },
}


def create_push_log_by_type(type: PushLogType, navigation_data=None):
    # 정의되지 않은 타입은 예외 처리
    if type not in PUSH_LOG_MESSAGES:
        raise ValueError(f"'{type}'에 대한 title/content 정의가 없습니다.")

    message = PUSH_LOG_MESSAGES[type]

    # navigation_data가 명시적으로 제공되지 않으면 기본값 사용
    nav_data = navigation_data if navigation_data is not None else message.get("navigation_data")

    return PushLog.objects.create(
        type=type,
        title=message["title"],
        content=message["content"],
        navigation_data=nav_data,
    )


def send_push(push_log: PushLog, user: User):
    logger.info(f"[DEBUG] send_push 시작 - PushLog ID: {push_log.id}, User ID: {user.id}")

    devices = Device.objects.filter(user=user)
    logger.info(f"[DEBUG] 유저 {user.id} 디바이스 조회 결과: {devices.count()}개")

    if devices.exists():
        for device in devices:
            logger.info(f"[DEBUG] 디바이스 추가: {device.id}, 토큰: {device.token[:20]}...")
        push_log.to_set.add(*devices)
        logger.info(f"[DEBUG] PushLog {push_log.id}에 디바이스 {devices.count()}개 추가됨")
    else:
        logger.warning(f"[DEBUG] 유저 {user.id}에게 디바이스가 없음!")
        return

    try:
        logger.info(f"[DEBUG] PushLog {push_log.id} 발송 시작...")
        push_log.send()
        logger.info(f"[DEBUG] PushLog {push_log.id} 발송 완료! 상태: {push_log.status}")

        if push_log.status == PushLogStatus.FAILURE:
            logger.error(f"[DEBUG] PushLog {push_log.id} 발송 실패 - 이유: {push_log.fail_reason}")

    except Exception as e:
        logger.error(f"[DEBUG] PushLog {push_log.id} 발송 중 예외 발생: {str(e)}")
        push_log.status = PushLogStatus.FAILURE
        push_log.fail_reason = f"PushLog Error: {str(e)}"
        push_log.save()
