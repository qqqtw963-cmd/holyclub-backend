from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.bible_version.v1.views import BibleVersionViewSet

router = DefaultRouter()
router.register("bible_version", BibleVersionViewSet, basename="bible_version")

urlpatterns = [
    path("", include(router.urls)),
]
