from django.urls import path

from app.terms_of_service.v1.views import CurrentTermsOfServiceView

urlpatterns = [
    path("terms_of_service/current/", CurrentTermsOfServiceView.as_view(), name="terms-of-service-current"),
]
