from rest_framework import serializers

from app.privacy_policy.models import PrivacyPolicy


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = [
            "id",
            "version",
            "content",
        ]
