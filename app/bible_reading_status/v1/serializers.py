from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.bible_reading_log.models import BibleReadingLog
from app.bible_reading_status.models import BibleReadingStatus
from app.common.validators import validate_serializer_request_user


class BibleReadingStatusSerializer(serializers.ModelSerializer):
    """해당 유저가 지금까지 읽은 내역에 대해서"""

    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    class Meta:
        model = BibleReadingStatus
        fields = [
            "id",
            "user",
            "book",
            "chapter",
            "count",
            # requset
            "local_datetime",
            # response
            "created_at",
            "updated_at",
            "timezone_offset",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
            "timezone_offset",
            "count",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)

        # ISO8601 형식 검증
        local_datetime = attrs.pop("local_datetime", None)
        if local_datetime.tzinfo is None:
            raise ValidationError(
                {"local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요. (예: 2024-01-15T14:30:00+09:00)"]}
            )

        utc_offset = local_datetime.utcoffset()
        attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60) if utc_offset else 0

        attrs["existing_instance"] = BibleReadingStatus.objects.filter(
            user=attrs["user"],
            book=attrs.get("book"),
            chapter=attrs.get("chapter"),
        ).first()

        # BibleReadingLog 생성을 위한 데이터 준비
        attrs["local_datetime"] = local_datetime

        return attrs

    def create(self, validated_data):
        existing_instance = validated_data.pop("existing_instance", None)
        local_datetime = validated_data.pop("local_datetime", None)

        # 기존 객체가 있으면 count 증가 및 updated_at 갱신
        if existing_instance:
            existing_instance.count += 1
            existing_instance.timezone_offset = validated_data["timezone_offset"]
            existing_instance.save()

            self._update_bible_reading_log(existing_instance, local_datetime)
            return existing_instance
        else:
            bible_reading_status = super().create(validated_data)
            self._update_bible_reading_log(bible_reading_status, local_datetime)
            return bible_reading_status

    def _update_bible_reading_log(self, bible_reading_status, local_datetime):
        """BibleReadingLog 생성 또는 업데이트"""
        created_at = local_datetime.astimezone(timezone.utc)

        utc_offset = local_datetime.utcoffset()
        timezone_offset = int(utc_offset.total_seconds() / 60) if utc_offset else 0

        local_date = local_datetime.date()

        # recognized_date 계산 (새벽 4시 기준)
        if local_datetime.hour < 4:
            recognized_date = local_datetime.date() - timedelta(days=1)
        else:
            recognized_date = local_datetime.date()

        # 중복 체크 후 생성
        existing_log = BibleReadingLog.objects.filter(
            user=bible_reading_status.user,
            recognized_date=recognized_date,
        ).first()

        if not existing_log:
            BibleReadingLog.objects.create(
                user=bible_reading_status.user,
                created_at=created_at,
                timezone_offset=timezone_offset,
                local_date=local_date,
                recognized_date=recognized_date,
            )
        else:
            existing_log.count += 1
            existing_log.save()
