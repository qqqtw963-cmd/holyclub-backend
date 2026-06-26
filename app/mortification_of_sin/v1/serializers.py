from datetime import timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from app.mortification_of_sin.models import MortificationOfSin, WeeklyMortificationOfSin, WeeklyMortificationOfSinSlot


class WeeklyMortificationOfSinSerializer(serializers.ModelSerializer):
    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")

    class Meta:
        model = WeeklyMortificationOfSin
        fields = [
            "id",
            "user",
            "slot",
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

        slot = attrs.get("slot")
        if WeeklyMortificationOfSin.objects.filter(
            user=request_user,
            week_start_sunday=week_start_sunday,
            slot=slot,
        ).exists():
            raise ValidationError({"slot": ["해당 주에 이미 죄와의 싸움1,2가 존재합니다."]})

        attrs["user"] = request_user
        attrs["week_start_sunday"] = week_start_sunday
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance


class MortificationOfSinSerializer(serializers.ModelSerializer):
    local_datetime = serializers.DateTimeField(write_only=True, help_text="사용자 디바이스의 현재 시간 (ISO8601 형식)")
    slot = serializers.ChoiceField(
        choices=WeeklyMortificationOfSinSlot.choices,
        write_only=True,
        help_text="죄와의 싸움 슬롯 (FIRST 또는 SECOND)",
    )

    class Meta:
        model = MortificationOfSin
        fields = [
            "id",
            "local_datetime",
            "slot",
            "score",
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

        # slot 가져오기
        slot = attrs.pop("slot", None)
        if not slot:
            raise ValidationError(
                {
                    "slot": ["슬롯(FIRST 또는 SECOND)을 지정해주세요."],
                }
            )

        # 특정 슬롯의 WeeklyMortificationOfSin 찾기
        weekly_mos = WeeklyMortificationOfSin.objects.filter(
            user=request_user,
            week_start_sunday=week_start_sunday,
            slot=slot,
        ).first()

        if not weekly_mos:
            raise ValidationError(
                {
                    "slot": [f"해당 주에 {slot} 슬롯의 죄와의 싸움이 등록되지 않았습니다. 먼저 주간 계획을 등록해주세요."],
                }
            )

        attrs["weekly_mos"] = weekly_mos

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
        weekly_mos = validated_data["weekly_mos"]
        recognized_date = validated_data["recognized_date"]

        mortification_of_sin, created = MortificationOfSin.objects.get_or_create(
            weekly_mos=weekly_mos,
            recognized_date=recognized_date,
            defaults={
                "score": validated_data.get("score"),
                "timezone_offset": validated_data["timezone_offset"],
                "local_date": validated_data["local_date"],
            },
        )

        if not created:
            # 기존 기록이 있으면 현재 request로 들어온 값들로 업데이트
            mortification_of_sin.score = validated_data.get("score")
            mortification_of_sin.timezone_offset = validated_data["timezone_offset"]
            mortification_of_sin.local_date = validated_data["local_date"]
            mortification_of_sin.save()

        return mortification_of_sin
