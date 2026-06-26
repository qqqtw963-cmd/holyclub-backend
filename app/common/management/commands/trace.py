import boto3
from django.conf import settings
from django.core.management.base import BaseCommand

from app.common.utils import color_string


class Command(BaseCommand):
    help = "트레이스를 검색합니다."

    def add_arguments(self, parser):
        parser.add_argument("trace_id", type=str, help="ID")

    def handle(self, *args, **options):
        trace_id = options["trace_id"]

        self.get_trace_log(trace_id)

    def get_trace_log(self, trace_id):
        cloudwatch_client = boto3.client("logs")
        next_token = None
        events = []
        params = {
            "logGroupName": settings.LOGGING["handlers"]["watchtower_info"]["log_group"],
            "filterPattern": f'"{trace_id}"',
            "startTime": int(trace_id.split("_")[0]) - 5000,
            "endTime": int(trace_id.split("_")[0]) + 5000,
        }
        while True:
            if next_token:
                params["nextToken"] = next_token
            response = cloudwatch_client.filter_log_events(**params)

            events.extend(response["events"])
            if events:
                break
            next_token = response.get("nextToken")
            if not next_token:
                break
        if events:
            print(color_string("red", events[0]["message"]))
        else:
            is_retry = input(color_string("red", "로그가 검색되지 않았습니다. 재검색을 원하시면 Y를 입력하세요. (기본: Y, 종료: 아무키)")) or "Y"
            if is_retry == "Y":
                self.get_trace_log(trace_id)
