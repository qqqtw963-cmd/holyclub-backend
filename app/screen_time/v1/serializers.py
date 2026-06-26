from rest_framework import serializers

from app.common.validators import validate_serializer_request_user
from app.screen_time.models import DailyScreenTimeLog


class DailyScreenTimeLogSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    minutes = serializers.IntegerField(min_value=0)

    class Meta:
        model = DailyScreenTimeLog
        fields = ["id", "date", "minutes"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)
        return attrs

    def create(self, validated_data):
        instance, _ = DailyScreenTimeLog.objects.update_or_create(
            user=validated_data["user"],
            date=validated_data["date"],
            defaults={"minutes": validated_data["minutes"]},
        )
        return instance
