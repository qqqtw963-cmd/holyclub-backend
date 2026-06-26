from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.pray_time_log.v1.views import PrayTimeLogViewSet

router = DefaultRouter()
router.register("pray_time_log", PrayTimeLogViewSet, basename="pray_time_log")

urlpatterns = [
    path("", include(router.urls)),
]
