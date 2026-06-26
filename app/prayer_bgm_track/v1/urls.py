from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.prayer_bgm_track.v1.views import PrayerBgmTrackViewSet

router = DefaultRouter()
router.register("prayer_bgm_track", PrayerBgmTrackViewSet, basename="prayer_bgm_track")

urlpatterns = [
    path("", include(router.urls)),
]
