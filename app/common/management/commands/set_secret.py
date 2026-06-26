import json

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "AWS secret manager를 세팅합니다."

    def add_arguments(self, parser):
        parser.add_argument("secret_id", type=str, help="AWS secret id")
        parser.add_argument("key", type=str, help="AWS secret key")
        parser.add_argument("value", type=str, help="AWS secret value")

    def handle(self, *args, **options):
        secret_id = options.get("secret_id")
        key = options.get("key")
        value = options.get("value").replace("\\n", "\n")

        self.update_secret_value(secret_id, key, value)

    @staticmethod
    def update_secret_value(secret_id, key, value):
        secrets_manager_client = boto3.client("secretsmanager")
        action = "추가"
        try:
            response = secrets_manager_client.get_secret_value(SecretId=secret_id)
            secret_string = json.loads(response["SecretString"])
            if key in secret_string:
                action = "수정"
        except ClientError as e:
            if getattr(e, "response")["Error"]["Code"] == "ResourceNotFoundException":
                secrets_manager_client.create_secret(Name=secret_id)
                print("새로운 보안 암호가 생성됐습니다.")
                secret_string = {}
            else:
                raise CommandError(e)

        secret_string.update({key: value})
        secrets_manager_client.update_secret(
            SecretId=secret_id,
            SecretString=json.dumps(secret_string),
        )
        print(f"'{secret_id}'에 '{key}: {value}'를 {action}했습니다.")
