from django.apps import AppConfig


class PrivacyPolicyConfig(AppConfig):
    name = "app.privacy_policy"

    def ready(self):
        import app.privacy_policy.signals
