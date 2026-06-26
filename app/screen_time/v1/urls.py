from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.screen_time.v1.views import DailyScreenTimeLogViewSet

router = DefaultRouter()
router.register("screen_time", DailyScreenTimeLogViewSet, basename="screen_time")

urlpatterns = [
    path("", include(router.urls)),
]
