from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.bible.v1.views import BibleViewSet

router = DefaultRouter()
router.register("bible", BibleViewSet, basename="bible")

urlpatterns = [
    path("", include(router.urls)),
]
