import json
import subprocess
import time

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "AWS session manager를 시작합니다."

    def add_arguments(self, parser):
        parser.add_argument("--port", "-p", default=str(settings.DATABASES["default"]["PORT"]), type=str, help="로컬 포트")

    def handle(self, *args, **options):
        settings_option = options.get("settings")
        if settings_option != "config.settings.prod":
            raise CommandError("The --settings option can't be used not 'config.settings.prod'.")
        port = options.get("port")
        instance_id = self.get_bastion_host_instance_id()
        self.start_session(instance_id, port)

    @staticmethod
    def get_bastion_host_instance_id():
        ec2_client = boto3.client("ec2")
        response = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "tag:aws:cloudformation:stack-name",
                    "Values": [f"{settings.PROJECT_NAME}-{settings.APP_ENV}-vpc"],
                },
                {"Name": "tag:aws:cloudformation:logical-id", "Values": ["BastionHost"]},
            ]
        )
        instance_id = response["Reservations"][-1]["Instances"][0]["InstanceId"]
        return instance_id

    def start_instance(self, instance_id):
        ec2_client = boto3.client("ec2")
        try:
            print("인스턴스 시작.")
            ec2_client.start_instances(InstanceIds=[instance_id])
        except ClientError:
            raise CommandError("인스턴스가 중지되는 중이라 시작할 수 없습니다. 잠시 후 다시 시도해주세요.")
        print("인스턴스 활성화 기다리는 중...")
        waiter = ec2_client.get_waiter("instance_running")
        try:
            waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 10, "MaxAttempts": 12})
            # time.sleep(10)
        except Exception:
            self.stop_instance(instance_id)
            raise CommandError("2분 동안 기다려도 인스턴스가 활성화되지 않았습니다. 인스턴스를 종료합니다.")

    @staticmethod
    def stop_instance(instance_id):
        ec2_client = boto3.client("ec2")
        print("인스턴스 중지.")
        ec2_client.stop_instances(InstanceIds=[instance_id])

    def start_session(self, instance_id, port):
        parameters = {
            "localPortNumber": [port],
            "portNumber": [str(settings.DATABASES["default"]["PORT"])],
            "host": [settings.DATABASES["default"]["HOST"]],
        }

        command = (
            f"aws ssm start-session --target {instance_id} "
            f"--document-name AWS-StartPortForwardingSessionToRemoteHost "
            f"--parameters '{json.dumps(parameters)}'"
        )
        try:
            self.start_instance(instance_id)
            print("세션 시작. 종료하려면 'Conrtol+C'를 눌러주세요")
            self.recursion_start_session(command)
        except KeyboardInterrupt:
            ec2_client = boto3.client("ec2")
            waiter = ec2_client.get_waiter("instance_running")
            waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 10, "MaxAttempts": 12})
            print("세션 중지.")
            self.stop_instance(instance_id)

    def recursion_start_session(self, command, retry=0):
        response = subprocess.call(command, shell=True)
        if response == 254:
            if retry > 10:
                raise KeyboardInterrupt()
            retry += 1
            print(f"인스턴스 완전 활성화까지 재시도 중...")
            time.sleep(2)
            self.recursion_start_session(command, retry)
