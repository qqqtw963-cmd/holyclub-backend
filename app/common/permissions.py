from django.conf import settings
from rest_framework import permissions


class IsCron(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.META.get("HTTP_X_API_KEY") == settings.SECRET_KEY
