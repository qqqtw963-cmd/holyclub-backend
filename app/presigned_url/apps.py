from django.apps import AppConfig

from app.presigned_url.utils import get_file_fields


class PreSignedUrlConfig(AppConfig):
    name = "app.presigned_url"

    def ready(self):
        get_file_fields()
