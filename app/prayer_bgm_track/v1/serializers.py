from rest_framework import serializers

from app.prayer_bgm_track.models import PrayerBgmListeningState, PrayerBgmTrack


class PrayerBgmTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerBgmTrack
        fields = [
            "id",
            "title",
            "audio_file",
            "thumbnail_image",
            "duration_seconds",
            "is_active",
        ]


class PrayerBgmListeningStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerBgmListeningState
        fields = [
            "id",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance


"""
“유저가 가장 최근에 들은 BGM”
last_log = (
    PrayerBgmListeningState.objects
    .filter(user=user)
    .order_by("-updated_at")  # 또는 "-created_at"
    .first()
)  # 이건 내가 선택해서 해당 객체만 보여주고

“해당 BGM을 어디까지 들었는지” : 는 내가 response의 값으로 내려주고
position = last_log.last_position_seconds

"""
