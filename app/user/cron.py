import logging
from datetime import timedelta

from django.utils import timezone

from app.common.views import CronView
from app.push_log.models import PushLog, PushLogStatus, PushLogType
from app.push_log.utils import create_push_log_by_type, send_push
from app.user.models import UserPushSettings

logger = logging.getLogger("request")


class UserPushSettingsCron(CronView):
    def cron(self):
        """
        2개의 push 알림을 발송
        1. 일요일 저녁 6시 통계 알림 (유저 디바이스 기준)
        2. 매일 유저가 설정한 시간에 데일리 체크 알림
        """

        current_utc_time = timezone.now()

        # 1. 일요일 저녁 6시 통계 알림
        self.send_sunday_statistics_notification(current_utc_time)

        # 2. 매일 유저 설정 시간 데일리 체크 알림
        self.send_daily_check_notification(current_utc_time)

    def send_sunday_statistics_notification(self, current_utc_time):
        """일요일 저녁 6시에 통계 알림 발송 (유저 디바이스 기준 시간, 주 1회)"""
        weekday = current_utc_time.weekday()  # 월요일=0, 일요일=6
        current_date = current_utc_time.date()

        if weekday == 6:  # 일요일인 경우에만
            # 통계 알림이 활성화되어 있는 유저들 조회
            push_settings = UserPushSettings.objects.filter(
                is_weekly_summary_alarm_enabled=True,
            ).select_related("user")

            for setting in push_settings:
                # 유저의 timezone_offset을 이용해 유저 로컬 시간 계산
                user_local_time = current_utc_time + timedelta(minutes=setting.timezone_offset)
                user_local_weekday = user_local_time.weekday()  # 유저 로컬 시간 기준 요일

                # 유저 로컬 시간 기준으로도 일요일인지 확인
                if user_local_weekday == 6:  # 유저 로컬 시간도 일요일인 경우만
                    # 유저 로컬 시간이 저녁 6시 정확히 맞거나 +5분까지 확인
                    local_time = user_local_time.time()
                    target_time_minutes = 18 * 60  # 18:00 = 1080분
                    current_local_minutes = local_time.hour * 60 + local_time.minute

                    # 시간 차이 계산 (현재시간 - 목표시간)
                    time_diff = current_local_minutes - target_time_minutes

                    if 0 <= time_diff <= 5:  # 18시 정확히 맞거나 +5분까지만
                        # 오늘 이미 해당 유저에게 통계 알림을 보냈는지 확인
                        today_sent = PushLog.objects.filter(
                            type=PushLogType.STATISTICS_NOTIFICATION,
                            to_set__user=setting.user,
                            created_at__date=current_date,
                        ).exists()

                        if not today_sent:
                            push_log = create_push_log_by_type(PushLogType.STATISTICS_NOTIFICATION)
                            send_push(push_log, setting.user)

    def send_daily_check_notification(self, current_utc_time):
        """매일 유저가 설정한 시간에 데일리 체크 알림 발송 (하루 1회)"""
        current_date = current_utc_time.date()
        logger.info(f"[DEBUG] send_daily_check_notification 실행 - 현재 UTC 시간: {current_utc_time}")

        push_settings = UserPushSettings.objects.filter(
            alarm_time__isnull=False,
        ).select_related("user")

        logger.info(f"[DEBUG] alarm_time이 설정된 유저 수: {push_settings.count()}")

        for setting in push_settings:
            alarm_time = setting.alarm_time
            user = setting.user
            current_time = current_utc_time.time()

            logger.info(f"[DEBUG] 유저 {user.id}({user.email})")
            logger.info(f"[DEBUG] - alarm_time (UTC): {alarm_time}")
            logger.info(f"[DEBUG] - 현재시간 (UTC): {current_time}")

            # UTC 기준으로 직접 비교 (이미 alarm_time은 UTC로 저장되어 있음)
            current_minutes = current_time.hour * 60 + current_time.minute
            alarm_minutes = alarm_time.hour * 60 + alarm_time.minute

            # 시간 차이 계산 (현재시간 - 알람시간, 자정 넘나드는 경우 고려)
            time_diff = current_minutes - alarm_minutes
            if time_diff < -720:  # 자정을 넘어가는 경우 (예: 알람 23:50, 현재 00:05)
                time_diff += 1440
            elif time_diff > 720:  # 자정을 넘어가는 경우 (예: 알람 00:05, 현재 23:50)
                time_diff -= 1440

            logger.info(f"[DEBUG] - 시간차이: {time_diff}분 (현재시간 - 알람시간)")

            # 알람시간 정확히 맞거나 +5분까지만 허용 (일찍 보내지 않음)
            if 0 <= time_diff <= 5:
                logger.info(f"[DEBUG] 유저 {user.id} - 알람 시간 범위 내!")

                # 성공한 알림만 체크 (실패한 경우 재시도 가능)
                today_sent_logs = PushLog.objects.filter(
                    type=PushLogType.DAILY_CHECK_NOTIFICATION,
                    to_set__user=setting.user,
                    created_at__date=current_date,
                )

                success_logs = today_sent_logs.filter(status=PushLogStatus.SUCCESS)

                logger.info(f"[DEBUG] 유저 {user.id} - 오늘 총 PushLog: {today_sent_logs.count()}개")
                logger.info(f"[DEBUG] 유저 {user.id} - 성공한 PushLog: {success_logs.count()}개")

                # 각 로그의 상태 출력
                for log in today_sent_logs:
                    logger.info(f"[DEBUG] - PushLog {log.id}: 상태={log.status}, 생성시간={log.created_at}")

                if not success_logs.exists():
                    logger.info(f"[DEBUG] 유저 {user.id} - 성공한 알림이 없으므로 푸시 발송!")

                    try:
                        logger.info(f"[DEBUG] 유저 {user.id} - create_push_log_by_type 시작...")
                        push_log = create_push_log_by_type(PushLogType.DAILY_CHECK_NOTIFICATION)
                        logger.info(f"[DEBUG] 유저 {user.id} - PushLog 생성 완료, ID: {push_log.id}")

                        logger.info(f"[DEBUG] 유저 {user.id} - send_push 호출 시작...")
                        send_push(push_log, setting.user)
                        logger.info(f"[DEBUG] 유저 {user.id} - send_push 호출 완료!")

                        logger.info(f"[DEBUG] 유저 {user.id} - 발송 완료, 상태: {push_log.status}")

                    except Exception as e:
                        logger.error(f"[DEBUG] 유저 {user.id} - 푸시 발송 중 예외 발생: {str(e)}")
                        import traceback

                        logger.error(f"[DEBUG] 상세 에러: {traceback.format_exc()}")
                else:
                    logger.info(f"[DEBUG] 유저 {user.id} - 이미 성공한 알림이 있어서 건너뜀")
            else:
                logger.info(f"[DEBUG] 유저 {user.id} - 알람 시간 범위 밖 ({time_diff}분)")
