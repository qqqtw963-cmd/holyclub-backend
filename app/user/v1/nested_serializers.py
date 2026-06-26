from rest_framework import serializers

from app.device.models import Device
from app.user.models import UserPushSettings


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["uid", "token"]
        extra_kwargs = {
            "uid": {"validators": None},
        }


class UserPushSettingsReadSerializer(serializers.ModelSerializer):
    """
    1. alarm_time 값이 있으면 '오늘의 체크 알림' on 해주시면 됩니다.
    2. '오늘의 체크 알림'을 off하면 request에서 alarm_local_time에 null 넣고 request 해주시면 됩니다.
    """

    class Meta:
        model = UserPushSettings
        fields = [
            "id",
            "is_weekly_summary_alarm_enabled",
            "alarm_time",
            "timezone_offset",
        ]
