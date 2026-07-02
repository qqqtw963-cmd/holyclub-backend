from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.bible.models import BibleReference
from app.bible.v1.verse_serializers import BibleReferenceDetailSerializer, BibleReferenceSerializer
from app.common.validators import validate_serializer_request_user
from app.testimony_journal.models import TestimonyJournal


class TestimonyJournalSerializer(serializers.ModelSerializer):
    bible_reference = BibleReferenceSerializer(required=False, allow_null=True)

    class Meta:
        model = TestimonyJournal
        fields = [
            "id",
            "user",
            "content",
            "bible_reference",
        ]
        read_only_fields = ["user"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["bible_reference"] = (
            BibleReferenceDetailSerializer(instance.bible_reference).data
            if instance.bible_reference
            else None
        )
        return data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)

        if self.context.get("request") and self.context["request"].method == "PUT":
            if self.instance and self.instance.user != request_user:
                raise ValidationError({"content": ["자신이 작성한 고백록만 수정할 수 있습니다."]})

        attrs["user"] = request_user
        return attrs

    def _upsert_bible_reference(self, bible_reference_data):
        if bible_reference_data is None:
            return None
        sanitized_data = {
            key: value
            for key, value in bible_reference_data.items()
            if not str(key).startswith("_")
        }
        reference, _created = BibleReference.objects.get_or_create(**sanitized_data)
        return reference

    def create(self, validated_data):
        bible_reference_data = validated_data.pop("bible_reference", None)
        validated_data["bible_reference"] = self._upsert_bible_reference(bible_reference_data)
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        bible_reference_data = validated_data.pop("bible_reference", serializers.empty)
        if bible_reference_data is not serializers.empty:
            validated_data["bible_reference"] = self._upsert_bible_reference(bible_reference_data)
        instance = super().update(instance, validated_data)
        return instance
