from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from app.prayer_journal.models import PrayerJournal


class PrayerJournalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerJournal
        fields = [
            "id",
            "title",
            "content",
            "start_date",
            "is_answered",
        ]


class PrayerJournalSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(
        required=False,
        # format="%Y-%m-%d",
        help_text="입력하면 해당 값으로 db에 저장하고, 입력값이 없으면 생성일 기준으로 db에 저장되도록",
    )
    answer_date = serializers.DateField(
        required=False,
        help_text="기도 응답 날짜 (PUT 요청시에만 사용 가능)",
    )

    class Meta:
        model = PrayerJournal
        fields = [
            "id",
            "title",
            "content",
            "start_date",
            "is_answered",
            "answer_date",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)

        # PUT 요청에서 is_answered와 answer_date의 관계 검증 및 처리
        if self.context.get("request") and self.context["request"].method == "PUT":
            is_answered = attrs.get("is_answered")
            answer_date = attrs.get("answer_date")

            if is_answered:
                if not answer_date:
                    raise ValidationError(
                        {
                            "answer_date": ["기도가 응답됨으로 표시되려면 응답 날짜가 필요합니다."],
                            "errorCode": [""],
                        }
                    )
            else:
                attrs["answer_date"] = None

        attrs["user"] = request_user
        return attrs

    def create(self, validated_data):
        # start_date가 제공되지 않으면 created_at 날짜 사용
        if "start_date" not in validated_data:
            validated_data["start_date"] = validated_data.get("created_at") or timezone.now().date()
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        if "start_date" not in validated_data:
            validated_data.pop("start_date", None)
        instance = super().update(instance, validated_data)
        return instance


class PrayerJournalAnsweredSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerJournal
        fields = [
            "id",
            "is_answered",
            "answer_date",
        ]
        read_only_fields = [
            "is_answered",
            "answer_date",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)

        instance = self.context["view"].get_object()
        if instance.user != request_user:
            raise ValidationError(
                {
                    "detail": ["본인이 생성한 기도제목에만 접근할 수 있습니다."],
                    "errorCode": ["PERMISSION_DENIED"],
                }
            )

        attrs["user"] = request_user
        attrs["instance"] = instance
        return attrs

    def create(self, validated_data):
        instance = validated_data.pop("instance")

        if instance.is_answered:
            instance.is_answered = False
            instance.answer_date = None
        else:
            instance.is_answered = True
            instance.answer_date = timezone.now().date()

        instance.save()
        return instance
