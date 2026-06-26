from django.apps import AppConfig


class WebsocketConnectionConfig(AppConfig):
    name = "app.websocket_connection"

    def ready(self):
        import app.websocket_connection.signals
