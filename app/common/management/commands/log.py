from datetime import datetime

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.common.utils import color_string


class Command(BaseCommand):
    help = "AWS CloudWatch 로그를 확인합니다."

    def handle(self, *args, **options):
        cloudwatch_client = boto3.client("logs")

        log_groups_response = cloudwatch_client.describe_log_groups(logGroupNamePrefix=settings.PROJECT_NAME)
        log_groups = log_groups_response["logGroups"]
        for i, group in enumerate(log_groups):
            print(color_string("blue", f"{i}: {group['logGroupName']}"))
        group_index = int(input(color_string("red", "로그 그룹 번호를 선택하세요: ")))
        log_group_arn = log_groups[group_index]["arn"][:-1]
        self.get_last_log(log_group_arn)
        self.get_tail_log(log_group_arn)

    def get_last_log(self, log_group_arn):
        cloudwatch_client = boto3.client("logs")
        log_streams_response = cloudwatch_client.describe_log_streams(logGroupIdentifier=log_group_arn, descending=True)
        log_stream_name = log_streams_response["logStreams"][0]["logStreamName"]
        response = cloudwatch_client.get_log_events(
            logGroupIdentifier=log_group_arn,
            logStreamName=log_stream_name,
            limit=100,
        )
        for log_event in response["events"]:
            print(
                "{date} {log}".format(
                    date=color_string(
                        "cyan",
                        f"[{timezone.make_aware(timezone.datetime.fromtimestamp(log_event['timestamp'] / 1000))}]",
                    ),
                    log=color_string("white", log_event["message"]),
                )
            )

    def get_tail_log(self, log_group_arn):
        cloudwatch_client = boto3.client("logs")
        response = cloudwatch_client.start_live_tail(logGroupIdentifiers=[log_group_arn])
        try:
            for event in response["responseStream"]:
                if "sessionStart" in event:
                    pass
                elif "sessionUpdate" in event:
                    log_events = event["sessionUpdate"]["sessionResults"]
                    for log_event in log_events:
                        print(
                            "{date} {log}".format(
                                date=color_string("cyan", f"[{datetime.fromtimestamp(log_event['timestamp'] / 1000)}]"),
                                log=color_string("white", log_event["message"]),
                            )
                        )
                else:
                    raise RuntimeError(str(event))
        except KeyboardInterrupt:
            print(color_string("red", "로그 스트림을 종료합니다."))
