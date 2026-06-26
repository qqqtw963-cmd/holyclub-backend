from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.dash_board.v1.views import DashBoardViewSet

router = DefaultRouter()
router.register("dash_board", DashBoardViewSet, basename="dash_board")

urlpatterns = [
    path("", include(router.urls)),
]
