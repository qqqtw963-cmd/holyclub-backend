from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from app.mortification_of_sin.models import WeeklyMortificationOfSin


class MortificationOfSinPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        # create 액션에서 weekly_sd 권한 확인
        if request.method == "POST" and view.action == "create":
            weekly_sd_id = request.data.get("weekly_sd")
            if weekly_sd_id:
                try:
                    weekly_sd = WeeklyMortificationOfSin.objects.get(id=weekly_sd_id)
                    if weekly_sd.user != request.user:
                        return False
                except WeeklyMortificationOfSin.DoesNotExist:
                    return False

        return True

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
