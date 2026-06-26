from rest_framework import serializers

from app.common.validators import validate_serializer_request_user
from app.sermon.models import Sermon, SermonBookmark, SermonWatch
from app.sermon.v1.nested_serializers import SermonSundayPreacherSerializer


class SermonSerializer(serializers.ModelSerializer):
    is_watched = serializers.BooleanField(default=False, label="시청 여부")  # annotate
    is_bookmarked = serializers.BooleanField(default=False, label="북마크 여부")
    sunday_preacher = SermonSundayPreacherSerializer(read_only=True)

    class Meta:
        model = Sermon
        fields = [
            "id",
            "youtube_link",
            "title",
            "content",
            "preached_date",
            "is_watched",
            "is_bookmarked",
            # filtering 잘 되었는지 보기 위해서
            "worship_type",
            "sunday_preacher",
            "overnight_worship_type",
        ]


class SermonWatchSerializer(serializers.ModelSerializer):
    """
    양방향 / 토글
    """

    class Meta:
        model = SermonWatch
        fields = [
            "id",
            "sermon",
            "user",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sermon",
            "user",
            "created_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)
        attrs["sermon"] = self.context["sermon"]
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        sermon = validated_data["sermon"]

        watch = SermonWatch.objects.filter(user=user, sermon=sermon).first()

        if watch:
            watch.delete()
            self._deleted = True
            return watch
        else:
            watch = SermonWatch.objects.create(user=user, sermon=sermon)
            self._deleted = False
            return watch

    def to_representation(self, instance):
        if getattr(self, "_deleted", False):
            return {}
        return super().to_representation(instance)


class SermonBookmarkSerializer(serializers.ModelSerializer):
    """
    양방향 / 토글
    """

    class Meta:
        model = SermonBookmark
        fields = [
            "id",
            "sermon",
            "user",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sermon",
            "user",
            "created_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)
        print("user123", attrs["user"])
        attrs["sermon"] = self.context["sermon"]
        print("sermon123", attrs["sermon"])
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        sermon = validated_data["sermon"]

        bookmark = SermonBookmark.objects.filter(user=user, sermon=sermon).first()

        if bookmark:
            bookmark.delete()
            self._deleted = True
            return bookmark
        else:
            bookmark = SermonBookmark.objects.create(user=user, sermon=sermon)
            self._deleted = False
            return bookmark

    def to_representation(self, instance):
        if getattr(self, "_deleted", False):
            return {}
        return super().to_representation(instance)
