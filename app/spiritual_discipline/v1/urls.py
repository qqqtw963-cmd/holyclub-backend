from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.spiritual_discipline.v1.views import SpiritualDisciplineViewSet

router = DefaultRouter()
router.register("spiritual_discipline", SpiritualDisciplineViewSet, basename="spiritual_discipline")

urlpatterns = [
    path("", include(router.urls)),
]
