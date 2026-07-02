import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
PROJECT_NAME = "holyclub"
SITE_NAME = "holyclub"
SITE_LOGO = "img/logo.png"
DOMAIN = os.environ.get("DOMAIN", "holyclub.co.kr")
SECRET_KEY = "test-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]
LANGUAGE_CODE = "ko"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_L10N = True
USE_TZ = True
APPEND_SLASH = False
AUTH_USER_MODEL = "user.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DEFAULT_HOST = "api"
ROOT_HOSTCONF = "config.hosts"
ROOT_URLCONF = "config.urls.api"
MIDDLEWARE = [
    "django_hosts.middleware.HostsRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
LOCAL_APPS = [
    "app.bible.apps.BibleConfig",
    "app.bible_version.apps.BibleVersionConfig",
    "app.bible_highlight.apps.BibleHighlightConfig",
    "app.bible_reading_status.apps.BibleReadingStatusConfig",
    "app.bible_reading_log.apps.BibleReadingLogConfig",
    "app.common.apps.CommonConfig",
    "app.daily_check_status.apps.DailyCheckStatusConfig",
    "app.dash_board.apps.DashBoardConfig",
    "app.device.apps.DeviceConfig",
    "app.email_log.apps.EmailLogConfig",
    "app.groups.apps.GroupsConfig",
    "app.home_content.apps.HomeContentConfig",
    "app.inquiry.apps.InquiryConfig",
    "app.mortification_of_sin.apps.MortificationOfSinConfig",
    "app.notification.apps.NotificationConfig",
    "app.pray_time_log.apps.PrayTimeLogConfig",
    "app.prayer_bgm_track.apps.PrayerBgmTrackConfig",
    "app.prayer_journal.apps.PrayerJournalConfig",
    "app.presigned_url.apps.PreSignedUrlConfig",
    "app.privacy_policy.apps.PrivacyPolicyConfig",
    "app.push_log.apps.PushLogConfig",
    "app.screen_time.apps.ScreenTimeConfig",
    "app.sermon.apps.SermonConfig",
    "app.sms_log.apps.SmsLogConfig",
    "app.spiritual_discipline.apps.SpiritualDisciplineConfig",
    "app.staticfile",
    "app.terms_of_service.apps.TermsOfServiceConfig",
    "app.testimony_journal.apps.TestimonyJournalConfig",
    "app.user.apps.UserConfig",
    "app.verifier.apps.VerifierConfig",
    "app.websocket_connection.apps.WebsocketConnectionConfig",
    "app.withdrawal_user.apps.WithdrawalUserConfig",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
    "django_hosts",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "ckeditor",
    "ckeditor_uploader",
    "ordered_model",
    "storages",
    "safedelete",
]
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]
INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["app.common.authentication.Authentication"],
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "app.common.pagination.LimitOffsetPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "app.common.filter_backends.FilterBackend",
        "app.common.filter_backends.OrderingFilter",
    ],
    "EXCEPTION_HANDLER": "app.common.views.exception_handler",
    "DEFAULT_SCHEMA_CLASS": "app.common.openapi.CustomAutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "NON_FIELD_ERRORS_KEY": "non_field",
    "ENABLE_LIST_MECHANICS_ON_NON_2XX": [400],
}
SPECTACULAR_SETTINGS = {
    "TITLE": f"{SITE_NAME} API",
    "DESCRIPTION": "test",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": "/v[0-9]",
    "DISABLE_ERRORS_AND_WARNINGS": True,
    "SORT_OPERATIONS": False,
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}
        }
    },
    "SECURITY": [{"Bearer": []}],
    "PREPROCESSING_HOOKS": ["app.common.spectacular_hooks.api_ordering"],
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "SORT_OPERATION_PARAMETERS": False,
}
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "_static"
MEDIA_ROOT = BASE_DIR / "_media"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": __import__("datetime").timedelta(days=1), "REFRESH_TOKEN_LIFETIME": __import__("datetime").timedelta(days=5), "ROTATE_REFRESH_TOKENS": True}
CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_CONFIGS = {"default": {"width": "100%"}}
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = "Asia/Seoul"
LOGGING = {"version": 1, "disable_existing_loggers": True}
