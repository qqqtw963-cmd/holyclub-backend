from rest_framework import serializers

from app.common.validators import validate_serializer_request_user
from app.inquiry.models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = [
            "id",
            "user",
            "title",
            "content",
        ]
        read_only_fields = ["user"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance
