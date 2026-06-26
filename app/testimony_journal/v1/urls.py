from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.testimony_journal.v1.views import TestimonyJournalViewSet

router = DefaultRouter()
router.register("testimony_journal", TestimonyJournalViewSet, basename="testimony_journal")

urlpatterns = [
    path("", include(router.urls)),
]
