import datetime

import django_filters

from app.pray_time_log.models import PrayTimeLog


class PrayTimeLogFilter(django_filters.FilterSet):
    local_datetime = django_filters.CharFilter(
        required=True,
        method="filter_by_local_datetime",
        help_text="사용자 디바이스의 현재 시간 (ISO8601 형식, 예: 2024-01-15T14:30:00+09:00)",
    )

    class Meta:
        model = PrayTimeLog
        fields = []

    def filter_by_local_datetime(self, queryset, name, value):
        # 빈 값 처리
        if not value or value.strip() == "":
            return queryset.none()

        try:
            # ISO8601 문자열을 파싱
            local_dt = datetime.datetime.fromisoformat(value.strip())

            # 사용자 로컬 시간 기준으로 날짜 계산
            local_time = local_dt.time()
            local_date = local_dt.date()

            # 새벽 4시 기준으로 recognized_date 결정
            if local_time < datetime.time(4, 0):
                # 4시 이전이면 전날로 인식
                recognized_date = local_date - datetime.timedelta(days=1)
            else:
                # 4시 이후면 당일로 인식
                recognized_date = local_date

            # recognized_date로 필터링
            return queryset.filter(recognized_date=recognized_date)

        except (ValueError, AttributeError, TypeError) as e:
            # 잘못된 형식인 경우 빈 쿼리셋 반환
            return queryset.none()
