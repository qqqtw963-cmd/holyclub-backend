from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from app.notification.models import Notification
from app.notification.v1.nested_serializers import NextNotificationSerializer, PrevNotificationSerializer


class NotificationSerializer(serializers.ModelSerializer):
    prev_obj = serializers.SerializerMethodField()
    next_obj = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "created_at",
            "title",
            "content",
            "prev_obj",
            "next_obj",
        ]

    @extend_schema_field(PrevNotificationSerializer)
    def get_prev_obj(self, obj):
        prev_obj = (
            Notification.objects.filter(
                created_at__lt=obj.created_at,
            )
            .order_by("-created_at")
            .first()
        )

        if prev_obj:
            return PrevNotificationSerializer(prev_obj, context=self.context).data
        return None

    @extend_schema_field(NextNotificationSerializer)
    def get_next_obj(self, obj):
        next_obj = (
            Notification.objects.filter(
                created_at__gt=obj.created_at,
            )
            .order_by("created_at")
            .first()
        )

        if next_obj:
            return NextNotificationSerializer(next_obj, context=self.context).data
        return None
