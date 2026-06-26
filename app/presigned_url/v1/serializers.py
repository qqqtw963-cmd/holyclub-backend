from django.apps import apps
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.presigned_url.utils import FIELD_CHOICES


class PresignedSerializer(serializers.Serializer):
    field_choice = serializers.ChoiceField(choices=FIELD_CHOICES, write_only=True)
    file_name = serializers.CharField(write_only=True)
    is_download = serializers.BooleanField(write_only=True)
    url = serializers.URLField(read_only=True)
    fields = serializers.JSONField(read_only=True)

    def validate(self, attrs):
        model, field_name = self.get_field_info(attrs.get("field_choice"))
        field = model._meta.get_field(field_name)
        if callable(field.upload_to):
            upload_to = field.upload_to(None, attrs["file_name"])
        else:
            upload_to = field.upload_to
        response = field.storage.generate_presigned_post(f"{upload_to}{attrs['file_name']}", attrs["is_download"])
        attrs.update(response)
        return attrs

    def create(self, validated_data):
        return validated_data

    def get_field_info(self, field_choice):
        app_label, model_name, field_name = field_choice.split(".")
        try:
            model = apps.get_model(app_label, model_name)
        except Exception as e:
            raise ValidationError("Invalid Model Data")
        return model, field_name
