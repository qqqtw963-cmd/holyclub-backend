from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import exception_handler as default_exception_handler

from app.common.permissions import IsCron


def exception_handler(exc, context):
    response = default_exception_handler(exc, context)
    return response


class CronView(APIView):
    permission_classes = [IsCron]

    def cron(self):
        raise NotImplemented("Not implemented yet")

    def post(self, request, *args, **kwargs):
        self.cron()
        return Response(status=status.HTTP_201_CREATED)
