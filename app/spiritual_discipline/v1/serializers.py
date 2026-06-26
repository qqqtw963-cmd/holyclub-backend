from datetime import timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from app.spiritual_discipline.models import SpiritualDiscipline, WeeklySpiritualDiscipline


class WeeklySpiritualDisciplineSerializer(serializers.ModelSerializer):
    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    class Meta:
        model = WeeklySpiritualDiscipline
        fields = [
            "id",
            "user",
            "practice",
            "local_datetime",
            "week_start_sunday",
        ]
        read_only_fields = [
            "user",
            "week_start_sunday",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)
        local_datetime = attrs.pop("local_datetime", None)

        # ISO8601 형식 검증
        if local_datetime.tzinfo is None:
            raise ValidationError(
                {"local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요. (예: 2024-01-15T14:30:00+09:00)"]}
            )

        local_date = local_datetime.date()
        week_start_sunday = local_date - timedelta(days=(local_date.weekday() + 1) % 7)

        if WeeklySpiritualDiscipline.objects.filter(
            user=request_user,
            week_start_sunday=week_start_sunday,
        ).exists():
            raise ValidationError({"week_start_sunday": ["해당 주에 이미 경건의 훈련이 등록되어 있습니다."]})

        attrs["user"] = request_user
        attrs["week_start_sunday"] = week_start_sunday
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance


class SpiritualDisciplineSerializer(serializers.ModelSerializer):
    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    class Meta:
        model = SpiritualDiscipline
        fields = [
            "id",
            "local_datetime",
            "timezone_offset",
            "local_date",
            "recognized_date",
        ]
        read_only_fields = [
            "timezone_offset",
            "local_date",
            "recognized_date",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)
        local_datetime = attrs.pop("local_datetime", None)

        # ISO8601 형식 검증
        if local_datetime.tzinfo is None:
            raise ValidationError(
                {
                    "local_datetime": ["timezone 정보가 필요합니다. ISO8601 형식으로 보내주세요. (예: 2024-01-15T14:30:00+09:00)"],
                }
            )

        # local_datetime가 속한 주의 시작일(일요일) 계산
        local_date = local_datetime.date()
        week_start_sunday = local_date - timedelta(days=(local_date.weekday() + 1) % 7)

        # WeeklySpiritualDiscipline 찾기
        weekly_sd = WeeklySpiritualDiscipline.objects.filter(
            user=request_user,
            week_start_sunday=week_start_sunday,
        ).first()

        if not weekly_sd:
            raise ValidationError(
                {
                    "local_datetime": ["해당 주에 등록된 경건의 습관이 없습니다. 먼저 주간 계획을 등록해주세요."],
                }
            )

        attrs["weekly_sd"] = weekly_sd

        # timezone_offset: 분 단위로 UTC와의 차이 계산
        utc_offset = local_datetime.utcoffset()
        attrs["timezone_offset"] = int(utc_offset.total_seconds() / 60) if utc_offset else 0

        # local_date: 사용자 타임존 기준 날짜
        attrs["local_date"] = local_date

        # recognized_date: 04:00 기준으로 인정되는 날짜 계산 (04:00 이전이면 전날로 인식)
        if local_datetime.hour < 4:
            recognized_date = local_datetime.date() - timedelta(days=1)
        else:
            recognized_date = local_datetime.date()

        attrs["recognized_date"] = recognized_date
        return attrs

    def create(self, validated_data):
        weekly_sd = validated_data["weekly_sd"]
        recognized_date = validated_data["recognized_date"]

        # 기존 기록이 있는지 확인
        existing_discipline = SpiritualDiscipline.objects.filter(
            weekly_sd=weekly_sd,
            recognized_date=recognized_date,
        ).first()

        if existing_discipline:
            # 기존 기록이 있으면 삭제하고 더미 객체 반환
            deleted_id = existing_discipline.id
            existing_discipline.delete()

            # 삭제된 객체의 정보를 담은 더미 객체 생성
            class DeletedInstance:
                def __init__(self, deleted_id):
                    self.id = deleted_id
                    self.deleted = True

            return DeletedInstance(deleted_id)
        else:
            # 기존 기록이 없으면 새로 생성
            discipline = SpiritualDiscipline.objects.create(
                weekly_sd=weekly_sd,
                recognized_date=recognized_date,
                timezone_offset=validated_data["timezone_offset"],
                local_date=validated_data["local_date"],
            )
            return discipline
