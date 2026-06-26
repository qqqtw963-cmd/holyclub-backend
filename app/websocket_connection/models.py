from django.db import models

from app.common.models import BaseModel


class WebsocketConnection(BaseModel):
    id = models.CharField(verbose_name="id", max_length=20, primary_key=True)
    user = models.ForeignKey("user.User", verbose_name="유저", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "websocket_connection"
        verbose_name = "웹소켓 연결"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
