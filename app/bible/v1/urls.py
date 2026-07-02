from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.bible.v1.reading_views import (
    BibleBookListAPIView,
    BibleChapterToggleReadAPIView,
    BibleProgressMapAPIView,
    ReadingPlanListCreateAPIView,
    ReadingPlanProgressAPIView,
)
from app.bible.v1.verse_views import BibleVerseRangeAPIView
from app.bible.v1.views import BibleViewSet

router = DefaultRouter()
router.register("bible", BibleViewSet, basename="bible")

urlpatterns = [
    path("bible/books/", BibleBookListAPIView.as_view()),
    path("bible/verses/", BibleVerseRangeAPIView.as_view()),
    path("bible/plans/", ReadingPlanListCreateAPIView.as_view()),
    path("bible/plans/<int:id>/progress/", ReadingPlanProgressAPIView.as_view()),
    path("bible/progress/", BibleProgressMapAPIView.as_view()),
    path("bible/chapters/<int:id>/toggle-read/", BibleChapterToggleReadAPIView.as_view()),
    path("", include(router.urls)),
]
