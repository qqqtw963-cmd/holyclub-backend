from django.urls import path

from app.privacy_policy.v1.views import CurrentPrivacyPolicyView

urlpatterns = [
    path("privacy_policy/current/", CurrentPrivacyPolicyView.as_view(), name="privacy-policy-current"),
]
