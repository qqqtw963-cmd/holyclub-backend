from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.bible_reading_log.v1.views import BibleReadingLogViewSet

router = DefaultRouter()
router.register("bible_reading_log", BibleReadingLogViewSet, basename="bible_reading_log")

urlpatterns = [
    path("", include(router.urls)),
]
