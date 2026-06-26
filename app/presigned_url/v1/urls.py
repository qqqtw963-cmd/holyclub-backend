from django.urls import path

from app.presigned_url.v1.views import PresignedUrlCreateView

urlpatterns = [
    path("presigned_url/", PresignedUrlCreateView.as_view()),
]
