from rest_framework import serializers

from app.notification.models import Notification


class PrevNotificationSerializer(serializers.ModelSerializer):
    # annotate된 필드 명시적 선언
    title = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
        ]


class NextNotificationSerializer(serializers.ModelSerializer):
    # annotate된 필드 명시적 선언
    title = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
        ]
