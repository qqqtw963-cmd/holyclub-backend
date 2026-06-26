import mimetypes
from urllib.parse import unquote

from storages.backends.s3boto3 import S3Boto3Storage


class DefaultMediaStorage(S3Boto3Storage):
    location = ""

    def url(self, name, format=None, **kwargs):
        return unquote(super().url(name, format, **kwargs))

    def generate_presigned_post(self, name, is_download=False):
        object_key = self.get_available_name(name)
        file_name = name.rsplit("/", 1)[-1]

        content_type, _ = mimetypes.guess_type(object_key)
        if content_type is None:
            content_type = "application/octet-stream"  # 기본값
        fields = {
            "Content-Type": content_type,
        }
        conditions = [
            {"Content-Type": content_type},
            ["content-length-range", 0, 20 * 1024 * 1024],
        ]  # 20MB  # 지정한 값과 같아야만 허용

        if is_download:
            fields.update(
                {"Content-Disposition": f"attachment; filename=\"{file_name}\"; filename*=UTF-8''{file_name}"}
            )
            conditions.append(
                {"Content-Disposition": f"attachment; filename=\"{file_name}\"; filename*=UTF-8''{file_name}"}
            )

        response = self.bucket.meta.client.generate_presigned_post(
            self.bucket.name,
            f"{self.location}/{object_key}",
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=360,
        )
        return response


class StaticStorage(S3Boto3Storage):
    endpoint_url = "https://s3.ap-northeast-2.amazonaws.com"
    location = "_static"
    file_overwrite = True
    querystring_auth = False


class PublicMediaStorage(DefaultMediaStorage):
    endpoint_url = "https://s3.ap-northeast-2.amazonaws.com"
    location = "_media/public"
    file_overwrite = False
    querystring_auth = False


class PrivateMediaStorage(DefaultMediaStorage):
    endpoint_url = "https://s3.ap-northeast-2.amazonaws.com"
    location = "_media/private"
    file_overwrite = False
    querystring_auth = True
