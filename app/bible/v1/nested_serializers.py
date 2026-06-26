from rest_framework import serializers

from app.bible_version.models import BibleVersion


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibleVersion
        fields = ["name"]
        ref_name = "BibleVersionSerializer"
