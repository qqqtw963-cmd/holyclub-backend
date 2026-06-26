from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.sermon.v1.views import SermonViewSet

router = DefaultRouter()
router.register("sermon", SermonViewSet, basename="sermon")

urlpatterns = [
    path("", include(router.urls)),
]
