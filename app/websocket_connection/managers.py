import json

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from app.websocket_connection.models import WebsocketConnection


class WebSocketManager:
    def __init__(self):
        self.apigw = boto3.client("apigatewaymanagementapi", endpoint_url=settings.WEBSOCKET_URL)

    def send(self, user_id, event, data):
        connection_set = WebsocketConnection.objects.filter(user_id=user_id)
        delete_connection_ids = []
        for connection in connection_set:
            try:
                self.apigw.post_to_connection(
                    ConnectionId=connection.id,
                    Data=json.dumps(
                        {
                            "event": event,
                            "data": data,
                        }
                    ),
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "GoneException":
                    delete_connection_ids.append(connection.id)
        if delete_connection_ids:
            WebsocketConnection.objects.filter(id__in=delete_connection_ids).delete()
