# required
# method: POST
# timezone: UTC
# cron expressions document
# https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cron-expressions.html
from django.urls import path

from app.user.cron import UserPushSettingsCron

SCHEDULES = dict(
    user_push_settings_cron={
        "path": path("cron/user_push_settings/", UserPushSettingsCron.as_view()),
        "cron": "* * * * ? *",  # 매 분 마다 실행
    },
    # schedule_name_3={
    #     "path": path("cron/withdrawal_user/", WithdrawalUserCron.as_view()),
    #     "cron": "0 0 * * ? *",
    # },
)
