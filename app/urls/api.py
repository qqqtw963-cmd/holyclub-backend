from django.urls import include, path

from app.user.cron import UserPushSettingsCron

urlpatterns = [
    path("v1/", include("app.bible.v1.urls")),
    path("v1/", include("app.bible_highlight.v1.urls")),
    path("v1/", include("app.bible_reading_status.v1.urls")),
    path("v1/", include("app.bible_reading_log.v1.urls")),
    path("v1/", include("app.daily_check_status.v1.urls")),
    path("v1/", include("app.dash_board.v1.urls")),
    path("v1/", include("app.groups.v1.urls")),
    path("v1/", include("app.inquiry.v1.urls")),
    path("v1/", include("app.mortification_of_sin.v1.urls")),
    path("v1/", include("app.notification.v1.urls")),
    path("v1/", include("app.pray_time_log.v1.urls")),
    path("v1/", include("app.prayer_bgm_track.v1.urls")),
    path("v1/", include("app.prayer_journal.v1.urls")),
    path("v1/", include("app.presigned_url.v1.urls")),
    path("v1/", include("app.privacy_policy.v1.urls")),
    path("v1/", include("app.screen_time.v1.urls")),
    path("v1/", include("app.sermon.v1.urls")),
    path("v1/", include("app.spiritual_discipline.v1.urls")),
    path("v1/", include("app.terms_of_service.v1.urls")),
    path("v1/", include("app.testimony_journal.v1.urls")),
    path("v1/", include("app.user.v1.urls")),
    path("v1/", include("app.verifier.v1.urls")),
    path("v1/", include("app.websocket_connection.v1.urls")),
    path("cron/user_push_settings/", UserPushSettingsCron.as_view(), name="cron_user_push_settings"),
    # path("cron/withdrawal_user/", WithdrawalUserCron.as_view(), name="cron_withdrawal_user"),  # todo
]
