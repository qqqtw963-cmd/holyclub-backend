import json
import logging
import random
import re
import string

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.utils import timezone
from rest_framework.exceptions import APIException

logger = logging.getLogger("request")


class SwaggerLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.content_type == "application/x-www-form-urlencoded"
            and re.match(r"/v(\d)/user/login/", request.path)
            and response.status_code == 201
        ):
            response.content = json.dumps(response.data, separators=(",", ":")).encode()
            response["Content-Length"] = str(int(response["Content-Length"]) + 2)

        return response


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # before
        request.trace_id = (
            str(int(timezone.localtime().timestamp() * 1000)) + "_" + "".join(random.choices(string.ascii_letters, k=4))
        )
        request_body = request.body

        # after
        response = self.get_response(request)
        response["X-Trace-Id"] = request.trace_id
        if request.path == "/_health/":
            return response
        if response.status_code >= 500:
            return response

        self._get_logger(response.status_code)(
            self._get_log_message(
                request.method,
                response.status_code,
                request.get_full_path(),
                request.user.id or 0,
                self._get_remote(request.META),
                request.trace_id,
                self._restore_request_body(request.content_type, request_body),
            )
        )
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied, SuspiciousOperation, APIException)):
            return None
        message = self._get_log_message(
            request.method,
            500,
            request.get_full_path(),
            request.user.id if request.user.id else 0,
            self._get_remote(request.META),
            request.trace_id,
            self._restore_request_body(request.content_type, request.body),
        )
        logger.error(message, exc_info=True)

    @staticmethod
    def _get_logger(status_code):
        if status_code < 400:
            return logger.info
        elif 400 <= status_code < 500:
            return logger.warning
        else:
            return logger.error

    @staticmethod
    def _get_log_message(method, status_code, path, user, remote, trace_id, body=None):
        return "HTTP {method} {status_code} {path} [{remote}] [{user}] [{trace_id}] {body}".format(
            method=method,
            status_code=status_code,
            path=path,
            user=user,
            remote=remote,
            trace_id=trace_id,
            body=body,
        )

    @staticmethod
    def _get_remote(meta):
        return f'{meta.get("HTTP_X_FORWARDED_FOR")}:{meta.get("HTTP_X_FORWARDED_PORT")}'

    @staticmethod
    def _restore_request_body(content_type, request_body):
        if content_type == "multipart/form-data":
            return ""
        if type(request_body) is bytes:
            request_body = request_body.decode()
        if request_body:
            request_body = f"\n{request_body}"
        return request_body


# class CsrfExemptMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         from django.conf import settings
#
#         exempt_urls = getattr(settings, "CSRF_EXEMPT_LIST", [])
#         path = request.path_info.lstrip("/")
#
#         for pattern in exempt_urls:
#             if re.match(pattern, path):
#                 setattr(request, "_dont_enforce_csrf_checks", True)
#                 break
