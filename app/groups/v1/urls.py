from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.groups.v1.views import GroupViewSet

router = DefaultRouter()
router.register("groups", GroupViewSet, basename="groups")

urlpatterns = [
    path("", include(router.urls)),
]
