from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.bible_reading_log.models import BibleReadingLog
from app.bible_reading_log.v1.nested_serializers import BibleReadingLogItemSerializer
from app.common.validators import validate_serializer_request_user


class BibleReadingLogListSerializer(serializers.Serializer):
    """성경 읽기 기록 목록"""

    count = serializers.IntegerField(help_text="총 기록 수")
    today_total_chapter_count = serializers.IntegerField(help_text="총 읽은 양")
    results = BibleReadingLogItemSerializer(many=True, help_text="읽기 기록들")


class BibleReadingLogSerializer(serializers.ModelSerializer):
    """
    데일리에 대해서 등록 (덮어씌우기)
    """

    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    class Meta:
        model = BibleReadingLog
        fields = [
            "id",
            "user",
            "count",
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
        """
        user와 recognized_date로 unique하게 묶음
        => 등록하거나 count값 업데이트
        """
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)

        # ISO8601 형식 검증
        local_datetime = attrs.pop("local_datetime", None)
        if local_datetime.tzinfo is None:
            raise ValidationError(
                {"local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요. (예: 2024-01-15T14:30:00+09:00)"]}
            )

        attrs["created_at"] = local_datetime.astimezone(timezone.utc)

        utc_offset = local_datetime.utcoffset()
        attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60) if utc_offset else 0

        attrs["local_date"] = local_datetime.date()

        if local_datetime.hour < 4:
            attrs["recognized_date"] = local_datetime.date() - timedelta(days=1)
        else:
            attrs["recognized_date"] = local_datetime.date()

        attrs["existing_log"] = BibleReadingLog.objects.filter(
            user=attrs["user"],
            recognized_date=attrs["recognized_date"],
        ).first()

        return attrs

    def create(self, validated_data):
        existing_log = validated_data.pop("existing_log", None)
        if existing_log:
            existing_log.count = validated_data["count"]
            existing_log.save()
            return existing_log
        else:
            return super().create(validated_data)
