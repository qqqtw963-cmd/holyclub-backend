import datetime
import os

import boto3
import requests

from config.settings.base import *

APP_ENV = "prod"
DEBUG = False
SECRET = get_secret(f"{PROJECT_NAME}/{APP_ENV}/django")
SECRET_KEY = SECRET["key"]

API_URL = f"https://api.{DOMAIN}"
WEBSOCKET_URL = f"https://ws.{DOMAIN}"

ALLOWED_HOSTS = [
    f"api.{DOMAIN}",
    f"admin.{DOMAIN}",
]
METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI")
if METADATA_URI:
    try:
        response = requests.get(METADATA_URI, timeout=0.1)
        data = response.json()
        ALLOWED_HOSTS.append(data["Networks"][0]["IPv4Addresses"][0])
    except Exception as e:
        print(e, "no ec2 instance")

CSRF_TRUSTED_ORIGINS = [f"https://admin.{DOMAIN}"]
# # API 경로는 CSRF 검증 제외
# CSRF_EXEMPT_LIST = [
#     r"^/v1/",  # v1으로 시작하는 모든 API 경로
# ]

CORS_ALLOWED_ORIGINS = [
    f"https://{DOMAIN}",
    f"https://www.{DOMAIN}",
    f"https://admin.{DOMAIN}",
    f"https://api.{DOMAIN}",
]
# CORS_ALLOW_ALL_ORIGINS = True

# # 모바일 앱 접근 허용
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_ALL_ORIGINS = False  # 보안을 위해 False 유지
#
# # Origin이 null인 경우를 위한 설정
# CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS


DATABASE_SECRET = get_secret(f"{PROJECT_NAME}/{APP_ENV}/db")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_SECRET["dbname"],
        "USER": DATABASE_SECRET["username"],
        "PASSWORD": DATABASE_SECRET["password"],
        "HOST": DATABASE_SECRET["host"],
        "PORT": DATABASE_SECRET["port"],
    },
    "reader": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_SECRET["dbname"],
        "USER": DATABASE_SECRET["username"],
        "PASSWORD": DATABASE_SECRET["password"],
        "HOST": DATABASE_SECRET["host"].replace(".cluster-", ".cluster-ro-"),
        "PORT": DATABASE_SECRET["port"],
    },
}


# CELERY
CELERY_BROKER_URL = f"sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": "ap-northeast-2",
    "queue_name_prefix": f"{PROJECT_NAME}-{APP_ENV}-",
}


# S3
AWS_REGION = "ap-northeast-2"
AWS_STORAGE_BUCKET_NAME = f"{PROJECT_NAME}-{APP_ENV}-bucket"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=864000"}
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_SECURE_URLS = True


# STORAGES
STORAGES = {
    "default": {
        "BACKEND": "app.common.storages.PublicMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "app.common.storages.StaticStorage",
    },
}

# MEDIA
MEDIAFILES_LOCATION = "_media"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/"

# STATIC
STATICFILES_LOCATION = "_static"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/"


# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}


boto3_client = boto3.client("logs", region_name="ap-northeast-2")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "cloudwatch": {
            "format": "%(message)s",
        },
    },
    "filters": {
        "sensitive": {
            "()": "config.filters.SensitiveFilter",
        },
    },
    "handlers": {
        "watchtower_info": {
            "level": "INFO",
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": boto3_client,
            "log_group": f"{PROJECT_NAME}/{APP_ENV}/info",
            "log_group_retention_days": 14,
            "stream_name": "web-{strftime:%Y-%m-%d}",
            "filters": ["sensitive"],
        },
        "watchtower_error": {
            "level": "ERROR",
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": boto3_client,
            "log_group": f"{PROJECT_NAME}/{APP_ENV}/error",
            "log_group_retention_days": 30,
            "stream_name": "web-{strftime:%Y-%m-%d}",
            "filters": ["sensitive"],
        },
    },
    "loggers": {
        "request": {
            "handlers": ["watchtower_info", "watchtower_error"],
            "level": "INFO",
        },
    },
}
