from rest_framework import serializers

from app.bible_highlight.models import BibleHighlight
from app.common.validators import validate_serializer_request_user


class BibleHighlightSerializer(serializers.ModelSerializer):
    """
    이미 객체가 존재해도 동일하게 post로 요청하면 됨 (색상 변경됨)
    sorting: verse의 오름차순 (책/장: 필터링 필수값)
    """

    class Meta:
        model = BibleHighlight
        fields = [
            "id",
            "user",
            "book",
            "chapter",
            "verse",
            "color",
        ]
        read_only_fields = [
            "user",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = validate_serializer_request_user(self, attrs)
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        book = validated_data["book"]
        chapter = validated_data["chapter"]
        verse = validated_data["verse"]
        color = validated_data["color"]

        instance, created = BibleHighlight.objects.update_or_create(
            user=user,
            book=book,
            chapter=chapter,
            verse=verse,
            defaults={"color": color},
        )
        return instance
