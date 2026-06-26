from rest_framework import serializers

from app.bible.models import Bible
from app.bible.v1.nested_serializers import VersionSerializer


class BibleSerializer(serializers.ModelSerializer):
    version_set = VersionSerializer(label="버전", many=True)

    class Meta:
        model = Bible
        fields = [
            "data",
            "updated_at",
            "version_set",
        ]
