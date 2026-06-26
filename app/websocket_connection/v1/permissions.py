from django.conf import settings
from rest_framework import permissions


class WebsocketConnectionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.data["api_key"] == settings.SECRET_KEY

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
