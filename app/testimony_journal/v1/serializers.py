from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.common.validators import validate_serializer_request_user
from app.testimony_journal.models import TestimonyJournal


class TestimonyJournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestimonyJournal
        fields = [
            "id",
            "user",
            "content",
        ]
        read_only_fields = ["user"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)

        if self.context.get("request") and self.context["request"].method == "PUT":
            if self.instance and self.instance.user != request_user:
                raise ValidationError({"content": ["자신이 작성한 고백록만 수정할 수 있습니다."]})

        attrs["user"] = request_user
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance
