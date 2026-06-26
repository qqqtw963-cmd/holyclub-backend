from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.bible_reading_status.v1.views import BibleReadingStatusViewSet

router = DefaultRouter()
router.register("bible_reading_status", BibleReadingStatusViewSet, basename="bible_reading_status")

urlpatterns = [
    path("", include(router.urls)),
]
