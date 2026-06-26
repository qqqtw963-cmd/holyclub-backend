from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from app.daily_check_status.models import DailyCheckStatus


class DailyCheckStatusSerializer(serializers.ModelSerializer):
    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    class Meta:
        model = DailyCheckStatus
        fields = [
            "id",
            "user",
            "check_type",
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
        check_type = attrs["check_type"]

        # ISO8601 형식 검증
        local_datetime = attrs.pop("local_datetime", None)
        if local_datetime.tzinfo is None:
            raise ValidationError(
                {"local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요. (예: 2024-01-15T14:30:00+09:00)"]}
            )

        # created_at: local_datetime을 UTC로 변환하여 저장
        attrs["created_at"] = local_datetime.astimezone(timezone.utc)

        # timezone_offset: 분 단위로 UTC와의 차이 계산
        utc_offset = local_datetime.utcoffset()
        attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60) if utc_offset else 0

        # local_date: 사용자 타임존 기준 날짜
        attrs["local_date"] = local_datetime.date()

        # recognized_date: 04:00 기준으로 인정되는 날짜 계산 (04:00 이전이면 전날로 인식)
        if local_datetime.hour < 4:
            recognized_date = local_datetime.date() - timedelta(days=1)
        else:
            recognized_date = local_datetime.date()

        attrs["user"] = request_user
        attrs["recognized_date"] = recognized_date
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        check_type = validated_data["check_type"]
        recognized_date = validated_data["recognized_date"]

        existing_record = DailyCheckStatus.objects.filter(
            user=user,
            check_type=check_type,
            recognized_date=recognized_date,
        ).first()

        if existing_record:
            existing_record.delete()
            self._deleted = True
            return existing_record
        else:
            instance = super().create(validated_data)
            self._deleted = False
            return instance

    def to_representation(self, instance):
        if getattr(self, "_deleted", False):
            return {}
        return super().to_representation(instance)
