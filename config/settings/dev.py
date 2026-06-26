import datetime

import boto3

from config.settings.base import *

APP_ENV = "dev"
DEBUG = True
SECRET = get_secret(f"{PROJECT_NAME}/{APP_ENV}/django")
SECRET_KEY = SECRET["key"]

API_URL = f"https://api.{APP_ENV}.{DOMAIN}"
WEBSOCKET_URL = f"https://ws.{APP_ENV}.{DOMAIN}"

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [f"https://admin.{APP_ENV}.{DOMAIN}"]
CORS_ALLOW_ALL_ORIGINS = True


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
}


# S3
AWS_REGION = "ap-northeast-2"
AWS_STORAGE_BUCKET_NAME = f"{PROJECT_NAME}-{APP_ENV}-bucket"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=864000"}
AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = "public-read"  # todo
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
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=5),
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
