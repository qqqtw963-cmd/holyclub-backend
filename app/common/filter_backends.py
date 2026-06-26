from django.utils.encoding import force_str
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.contrib.django_filters import DjangoFilterExtension
from rest_framework.filters import OrderingFilter as DjangoOrderingFilter


class CustomFilterBackendExtension(DjangoFilterExtension):
    target_class = "config.filter_backends.FilterBackend"


class FilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        filterset_class = None
        if view.action == "list":
            filterset_class = super().get_filterset_class(view, queryset)
        if hasattr(view, "get_filterset_class"):
            filterset_class = view.get_filterset_class()
        return filterset_class


class OrderingFilter(DjangoOrderingFilter):
    def remove_invalid_fields(self, queryset, fields, view, request):
        valid_fields = [item[0] for item in self.get_valid_fields(queryset, view, {"request": request})]
        return [term for term in fields if term in valid_fields]

    def get_schema_operation_parameters(self, view):
        ordering_fields = getattr(view, "ordering_fields", None)
        if not ordering_fields:
            return {}
        else:
            return [
                {
                    "name": self.ordering_param,
                    "required": False,
                    "in": "query",
                    "description": force_str(self.ordering_description),
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": view.ordering_fields,
                        },
                    },
                    "style": "simple",
                    "explode": False,
                },
            ]
