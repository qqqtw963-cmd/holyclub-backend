from rest_framework import serializers

from app.sermon.models import SundayPreacher


class SermonSundayPreacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SundayPreacher
        fields = [
            "id",
            "name",
        ]
