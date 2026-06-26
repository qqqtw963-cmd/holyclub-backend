from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.daily_check_status.v1.views import DailyCheckStatusViewSet

router = DefaultRouter()
router.register("daily_check_status", DailyCheckStatusViewSet, basename="daily_check_status")

urlpatterns = [
    path("", include(router.urls)),
]
