from rest_framework import serializers

from app.bible_version.models import BibleVersion
from app.common.validators import validate_serializer_request_user


class BibleVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibleVersion
        fields = [
            "id",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = validate_serializer_request_user(self, attrs)
        attrs["user"] = request_user
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance
