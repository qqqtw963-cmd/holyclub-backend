from rest_framework import serializers

from app.home_content.models import HomeContent


class HomeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeContent
        fields = [
            "id",
            "eyebrow",
            "main_title",
            "sub_title",
            "highlight_text",
            "cta_text",
            "cta_link",
            "is_active",
            "created_at",
            "updated_at",
        ]
