from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.prayer_journal.v1.views import PrayerJournalViewSet

router = DefaultRouter()
router.register("prayer_journal", PrayerJournalViewSet, basename="prayer_journal")

urlpatterns = [
    path("", include(router.urls)),
]
