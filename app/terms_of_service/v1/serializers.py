from rest_framework import serializers

from app.terms_of_service.models import TermsOfService


class TermsOfServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsOfService
        fields = [
            "id",
            "version",
            "content",
        ]
