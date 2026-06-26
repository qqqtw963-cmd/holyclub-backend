from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.bible_highlight.v1.views import BibleHighlightViewSet

router = DefaultRouter()
router.register("bible_highlight", BibleHighlightViewSet, basename="bible_highlight")

urlpatterns = [
    path("", include(router.urls)),
]
