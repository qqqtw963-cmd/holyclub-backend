from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from app.user.models import User


def validate_serializer_request_user(serializer, attrs: dict) -> User:
    request = serializer.context.get("request")
    if not request:
        raise AuthenticationFailed({"detail": "Request not found in serializer context"})
    request_user = request.user
    if request_user.is_authenticated:
        return request_user
    raise AuthenticationFailed({"detail": "Not authenticated"})


def validate_view_request_user(request) -> User:
    user = request.user
    if user.is_anonymous:
        raise NotAuthenticated()
    return user
