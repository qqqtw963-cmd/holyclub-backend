from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.inquiry.v1.views import InquiryViewSet

router = DefaultRouter()
router.register("inquiry", InquiryViewSet, basename="inquiry")

urlpatterns = [
    path("", include(router.urls)),
]
