import os
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials
from gunicorn.http import wsgi

from app.common.secrets import get_secret

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv(BASE_DIR / ".env")

PROJECT_NAME = "holyclub"
SITE_NAME = "holyclub"
SITE_LOGO = "img/logo.png"  # TODO: HolyClub branding asset로 교체
DOMAIN = os.environ.get("DOMAIN", "holyclub.co.kr")


class Response(wsgi.Response):
    def __init__(self, req, sock, cfg):
        super(Response, self).__init__(req, sock, cfg)
        self.version = PROJECT_NAME


wsgi.Response = Response


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
    # "django_celery_results",
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

MIDDLEWARE = [
    "config.middleware.SwaggerLoginMiddleware",
    "django_hosts.middleware.HostsRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "config.middleware.CsrfExemptMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.RequestLogMiddleware",
]


TEMPLATES = [
    {
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
    },
]

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "ko"

TIME_ZONE = "Asia/Seoul"
"""
request보낼때 무조건 ISO 기준으로 (타임존까지 포함해서)
"""

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


# APPEND_SLASH
APPEND_SLASH = False

# AUTH_USER_MODEL
AUTH_USER_MODEL = "user.User"

# APPLICATION
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# HOST
DEFAULT_HOST = "api"
ROOT_HOSTCONF = "config.hosts"
ROOT_URLCONF = "config.urls.api"


# MODEL ID
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# DATABASE ROUTER
DATABASE_ROUTERS = ["config.router.Router"]


# SIMPLE_JWT
SIMPLE_JWT_ALGORITHM = "HS256"


# DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "app.common.authentication.Authentication",
        # "rest_framework.authentication.TokenAuthentication",
    ],
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


# SPECTACULAR
SPECTACULAR_SETTINGS = {
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "TITLE": f"{SITE_NAME} API",
    "DESCRIPTION": f"""개발: [api.dev.{DOMAIN}](https://api.dev.{DOMAIN})<br/>운영: [api.{DOMAIN}](https://api.{DOMAIN})""",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": "/v[0-9]",
    "DISABLE_ERRORS_AND_WARNINGS": True,
    "SORT_OPERATIONS": False,
    "SWAGGER_UI_SETTINGS": {
        "docExpansion": "none",
        "defaultModelRendering": "model",
        "defaultModelsExpandDepth": 0,
        "deepLinking": True,
        "displayRequestDuration": True,
        "persistAuthorization": True,
        "syntaxHighlight.activate": True,
        "syntaxHighlight.theme": "agate",
        "showExtensions": True,
        "filter": True,
    },
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "Bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            },
        },
    },
    "SECURITY": [
        {
            "Bearer": [],
        }
    ],
    "PREPROCESSING_HOOKS": [
        "app.common.spectacular_hooks.api_ordering",
    ],
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "SORT_OPERATION_PARAMETERS": False,
}


# FILE_UPLOAD
DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200MB


# AWS SES
DEFAULT_FROM_EMAIL = f"noreply@{DOMAIN}"

# COOLSMS
COOLSMS_API_KEY = get_secret(f"{PROJECT_NAME}/key")["coolsms_api_key"]
COOLSMS_API_SECRET = get_secret(f"{PROJECT_NAME}/key")["coolsms_api_secret"]
COOLSMS_FROM_PHONE = "010-7509-7734"

# FIREBASE
FIREBASE_ENABLED = False
FIREBASE_INIT_ERROR = None
try:
    FIREBASE_CREDENTIAL_JSON = get_secret(f"{PROJECT_NAME}/firebase")
    cred = credentials.Certificate(FIREBASE_CREDENTIAL_JSON)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    FIREBASE_ENABLED = True
except Exception as e:
    FIREBASE_CREDENTIAL_JSON = None
    FIREBASE_INIT_ERROR = str(e)
    print(f"[WARN] Firebase disabled during settings load: {e}")


# CKEDITOR
CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_CONFIGS = {
    "default": {
        "width": "100%",
    },
    "legal": {
        "width": "100%",
        "toolbar": [
            ["Bold", "Italic", "Underline"],
            ["NumberedList", "BulletedList"],
            ["Link", "Unlink"],
            ["Font", "FontSize"],
            ["TextColor", "BGColor"],
            ["Source"],
        ],
        "removePlugins": "image,uploadimage,uploadfile,media,table",
    },
}


# CELERY
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = "Asia/Seoul"
CELERYD_SOFT_TIME_LIMIT = 300
CELERYD_TIME_LIMIT = CELERYD_SOFT_TIME_LIMIT + 60
CELERY_TASK_ACKS_LATE = True
CELERY_RESULT_BACKEND = "django-db"
CELERY_WORKER_MAX_TASKS_PER_CHILD = 500

# SOCIAL
SOCIAL_REDIRECT_PATH = "/social/callback"

# KAKAO
KAKAO_CLIENT_ID = get_secret(f"{PROJECT_NAME}/key")["kakao_client_id"]
KAKAO_CLIENT_SECRET = get_secret(f"{PROJECT_NAME}/key")["kakao_client_secret"]
KAKAO_LOGIN_URL = "https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={kakao_client_id}&redirect_uri={SOCIAL_REDIRECT_URL}&state=kakao"

# APPLE
APPLE_CLIENT_ID = "auth.holyclub.app"  # HolyClub Apple Service ID (웹/코드 교환용)
APPLE_APP_ID = "com.parkseongjeon.holyclub"  # HolyClub iOS bundle ID (native Sign in with Apple)
APPLE_CLIENT_SECRET = get_secret(f"{PROJECT_NAME}/key")["apple_client_secret"]
APPLE_KEY_ID = get_secret(f"{PROJECT_NAME}/key")["apple_key_id"]
APPLE_TEAM_ID = get_secret(f"{PROJECT_NAME}/key")["apple_team_id"]
APPLE_LOGIN_URL = "https://appleid.apple.com/auth/authorize?response_type=code&client_id={apple_client_id}&redirect_uri={SOCIAL_REDIRECT_URL}&state=apple"

# GOOGLE
GOOGLE_CLIENT_IDS = [client_id.strip() for client_id in os.getenv("GOOGLE_CLIENT_IDS", "").split(",") if client_id.strip()]
