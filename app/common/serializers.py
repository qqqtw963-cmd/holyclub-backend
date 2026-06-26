import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers


class PresignedSerializer(serializers.Serializer):
    file_name = serializers.CharField(write_only=True)
    url = serializers.URLField(read_only=True)
    fields = serializers.JSONField(read_only=True)

    def validate(self, attrs):
        response = self.create_presigned_post(attrs["file_name"])
        attrs.update(response)

        return attrs

    def create(self, validated_data):
        return validated_data

    def create_presigned_post(self, file_name):
        s3_config = Config(
            region_name="ap-northeast-2",
            signature_version="s3v4",
        )
        s3_client = boto3.client("s3", config=s3_config)
        ext = file_name.split(".")[-1]
        now = timezone.localtime()
        object_key = "/".join(
            [f"{self.context['view'].basename}/{now.year}/{now.month}/{now.day}", f"{uuid.uuid4()}.{ext}"]
        )
        response = s3_client.generate_presigned_post(
            settings.AWS_STORAGE_BUCKET_NAME,
            object_key,
            Conditions=[
                ["content-length-range", 0, 20971520],  # 20MB
                ["starts-with", "$Content-Type", f"image/"],
            ],
            ExpiresIn=360,
        )
        return response
