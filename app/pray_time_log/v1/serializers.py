from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from app.pray_time_log.models import PrayTimeLog, PrayType


class PrayTimeLogSerializer(serializers.ModelSerializer):
    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")
    duration_seconds = serializers.IntegerField(required=False, label="타이머/수동 일 때만 값을 넣어줍니다. (스톱워치일 때는 X)")

    class Meta:
        model = PrayTimeLog
        fields = [
            "id",
            "user",
            "type",
            "started_time",
            "ended_time",
            "duration_seconds",
            "local_datetime",  # requset용
            "created_at",
            "timezone_offset",
            "local_date",
            "recognized_date",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "timezone_offset",
            "local_date",
            "recognized_date",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)

        # ISO8601 형식 검증
        local_datetime = attrs.pop("local_datetime", None)
        if local_datetime.tzinfo is None:
            raise ValidationError(
                {"local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요. (예: 2024-01-15T14:30:00+09:00)"]}
            )

        # local_datetime을 local_date로 변환
        attrs["local_date"] = local_datetime.date()

        pray_type = attrs.get("type")
        started_time = attrs.get("started_time")
        ended_time = attrs.get("ended_time")
        duration_seconds = attrs.get("duration_seconds")

        if pray_type == PrayType.STOPWATCH:
            # 스톱워치: started_time과 ended_time 필수, duration_seconds 자동 계산
            if not started_time:
                raise ValidationError({"started_time": ["스톱워치 타입일 때는 시작 시간이 필요합니다."]})
            if not ended_time:
                raise ValidationError({"ended_time": ["스톱워치 타입일 때는 종료 시간이 필요합니다."]})

            # duration_seconds 자동 계산
            start_datetime = datetime.combine(local_datetime.date(), started_time)
            end_datetime = datetime.combine(local_datetime.date(), ended_time)

            # 자정을 넘긴 경우 처리 (ended_time이 started_time보다 작은 경우)
            if ended_time < started_time:
                end_datetime += timedelta(days=1)

            duration = end_datetime - start_datetime
            attrs["duration_seconds"] = int(duration.total_seconds())

        elif pray_type in [PrayType.TIMER, PrayType.MANUAL]:
            # 타이머/수동입력: duration_seconds 필수, started_time/ended_time은 null
            if duration_seconds is None:
                raise ValidationError({"duration_seconds": ["타이머/수동입력 타입일 때는 기도 시간(초)이 필요합니다."]})
            if duration_seconds <= 0:
                raise ValidationError({"duration_seconds": ["기도 시간은 0보다 커야 합니다."]})

            # started_time, ended_time은 null로 설정
            attrs["started_time"] = None
            attrs["ended_time"] = None

        # created_at: local_datetime을 UTC로 변환하여 저장
        attrs["created_at"] = local_datetime.astimezone(timezone.utc)

        # timezone_offset: 분 단위로 UTC와의 차이 계산
        utc_offset = local_datetime.utcoffset()
        attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60) if utc_offset else 0

        # local_date: 사용자 타임존 기준 날짜
        attrs["local_date"] = local_datetime.date()

        # recognized_date: 04:00 기준으로 인정되는 날짜 계산 (04:00 이전이면 전날로 인식)
        if local_datetime.hour < 4:
            attrs["recognized_date"] = local_datetime.date() - timedelta(days=1)
        else:
            attrs["recognized_date"] = local_datetime.date()

        attrs["user"] = request_user
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance
