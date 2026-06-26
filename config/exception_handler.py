from rest_framework import status
from rest_framework.exceptions import APIException


class SocialUserNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        self.detail = {"register_token": detail}
