from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.notification.v1.views import NotificationViewSet

router = DefaultRouter()
router.register("notification", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]
