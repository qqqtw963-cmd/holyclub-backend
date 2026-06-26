from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.mortification_of_sin.v1.views import MortificationOfSinViewSet

router = DefaultRouter()
router.register("mortification_of_sin", MortificationOfSinViewSet, basename="mortification_of_sin")

urlpatterns = [
    path("", include(router.urls)),
]
