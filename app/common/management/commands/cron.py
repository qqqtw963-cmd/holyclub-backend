import boto3
from django.conf import settings
from django.core.management import BaseCommand

from app.common.utils import color_string
from config.schedules import SCHEDULES


class Command(BaseCommand):
    help = "cron을 등록합니다."

    def handle(self, *args, **options):
        self._delete_rule(SCHEDULES.keys())
        for name, value in SCHEDULES.items():
            self._update_or_create_rule(name, str(value["path"].pattern), value["cron"])

    def _delete_rule(self, names):
        event_client = boto3.client("events", region_name="ap-northeast-2")
        prefix = f"{settings.PROJECT_NAME}-{settings.APP_ENV}-"
        rules = event_client.list_rules(NamePrefix=prefix, Limit=100)["Rules"]
        for rule in rules:
            name = rule["Name"].replace(prefix, "")
            if name not in names:
                print(color_string("red", f"'{name}' 스케줄이 제거됐습니다."))
                event_client.remove_targets(
                    Rule=rule["Arn"].split("/", 1)[-1],
                    Ids=[rule["Name"]],
                )
                event_client.delete_rule(Name=rule["Name"])

    def _update_or_create_rule(self, name, path, cron_expression):
        iam_client = boto3.client("iam", region_name="ap-northeast-2")
        event_client = boto3.client("events", region_name="ap-northeast-2")
        prefix = f"{settings.PROJECT_NAME}-{settings.APP_ENV}-"
        rule_name = prefix + name

        api_destination_name = f"{prefix}api-destination"
        api_destination_arn = event_client.describe_api_destination(Name=api_destination_name)["ApiDestinationArn"]

        role = iam_client.get_role(RoleName=f"{prefix}InvokeApiDestinationRole")["Role"]

        rule = event_client.put_rule(
            Name=rule_name,
            ScheduleExpression=f"cron({cron_expression})",
            State="ENABLED",
        )

        event_client.update_api_destination(
            Name=api_destination_name,
            InvocationEndpoint=f"{settings.API_URL}/*",
        )

        event_client.put_targets(
            Rule=rule["RuleArn"].split("/", 1)[-1],
            Targets=[
                {
                    "Id": rule_name,
                    "Arn": api_destination_arn,
                    "RoleArn": role["Arn"],
                    "HttpParameters": {
                        "PathParameterValues": [path],
                    },
                }
            ],
        )
        print(color_string("green", f"'{name}' 스케줄이 등록됐습니다. {cron_expression}"))
