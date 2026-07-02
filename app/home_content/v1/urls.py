from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.home_content.v1.views import HomeContentViewSet

router = DefaultRouter()
router.register("home_content", HomeContentViewSet, basename="home-content")

urlpatterns = [
    path("", include(router.urls)),
]
