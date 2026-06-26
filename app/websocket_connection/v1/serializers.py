from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from app.websocket_connection.models import WebsocketConnection


class WebsocketConnectionSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(write_only=True, allow_null=True)

    class Meta:
        model = WebsocketConnection
        fields = [
            "id",
            "access_token",
        ]

    def validate(self, attrs):
        if attrs.pop("access_token", None):
            try:
                token = AccessToken(token=attrs["access_token"])
            except TokenError as e:
                raise ValidationError(e)
            attrs["user_id"] = token.payload["user_id"]
        return attrs


class WebsocketDisconnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsocketConnection
        fields = ["id"]
        extra_kwargs = {
            "id": {"validators": []},
        }

    def create(self, validated_data):
        WebsocketConnection.objects.filter(id=validated_data["id"]).delete()
        return validated_data
