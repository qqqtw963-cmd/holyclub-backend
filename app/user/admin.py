from datetime import datetime, timedelta

from django.contrib import admin
from django.utils import timezone

from app.user.models import Device, User, UserPushSettings
from app.withdrawal_user.models import WithdrawalUser


class DeviceInline(admin.TabularInline):
    model = Device
    fields = ["uid", "token", "created_at", "updated_at"]
    readonly_fields = ["uid", "token", "created_at", "updated_at"]


class UserPushSettingsInline(admin.StackedInline):
    model = UserPushSettings
    fields = [
        "is_weekly_summary_alarm_enabled",
        "alarm_local_time",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "alarm_local_time",
        "created_at",
        "updated_at",
    ]
    extra = 0
    max_num = 1

    def alarm_local_time(self, obj):
        """alarm_time과 timezone_offset을 조합하여 로컬 시간 표시"""
        if not obj.alarm_time:
            return "-"

        # UTC 시간을 datetime으로 변환
        utc_datetime = datetime.combine(datetime.today().date(), obj.alarm_time)

        # timezone_offset을 적용하여 로컬 시간 계산
        local_datetime = utc_datetime + timedelta(minutes=obj.timezone_offset)

        return local_datetime.strftime("%H:%M")

    alarm_local_time.short_description = "알림 시간 (로컬)"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [
        DeviceInline,
        UserPushSettingsInline,
    ]

    list_display = [
        "id",
        "name",
        "phone",
        "church_name",
        "date_joined",
    ]
    list_filter = ["residence"]
    exclude = [
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "last_login",
        "user_permissions",
        "password",
    ]
    readonly_fields = [
        "email",
        "date_joined",
        "social_kind",
    ]
    search_fields = [
        "name",
        "phone",
        "church_name",
    ]
    search_help_text = "이름 또는 휴대폰 번호, 출석교회 로 검색해 주세요."

    filter_horizontal = ["groups"]

    def has_add_permission(self, request):
        return False

    def delete_model(self, request, obj):
        WithdrawalUser.objects.create(
            email=obj.email,
            name=obj.name,
            gender=obj.gender,
            birth_date=obj.birth_date,
            phone=obj.phone,
            church_name=obj.church_name,
            user_created_at=obj.date_joined,
            deleted_at=timezone.now(),
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            WithdrawalUser.objects.create(
                email=obj.email,
                name=obj.name,
                gender=obj.gender,
                birth_date=obj.birth_date,
                phone=obj.phone,
                church_name=obj.church_name,
                user_created_at=obj.date_joined,
                deleted_at=timezone.now(),
            )
        super().delete_queryset(request, queryset)

    def save_form(self, request, form, change):
        input_password = request.POST.get("password")
        instance = super().save_form(request, form, change)

        if not change:  # create
            instance.set_password(input_password)
        else:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            if input_password and not input_password == obj.password:  # input이 있고 변경되었을 때
                instance.set_password(input_password)
        instance.save()

        return instance


# @admin.register(UserPushSettings)
# class UserPushSettingsAdmin(admin.ModelAdmin):
#     list_display = [
#         "id",
#         "user",
#         "is_weekly_summary_alarm_enabled",
#         "alarm_time",
#         "alarm_local_time",
#         "timezone_offset",
#         "created_at",
#     ]
#     list_filter = [
#         "is_weekly_summary_alarm_enabled",
#         "timezone_offset",
#         "created_at",
#     ]
#     search_fields = [
#         "user__name",
#         "user__phone",
#         "user__email",
#     ]
#     readonly_fields = [
#         "alarm_local_time",
#         "created_at",
#         "updated_at",
#     ]
#
#     def alarm_local_time(self, obj):
#         """alarm_time과 timezone_offset을 조합하여 로컬 시간 표시"""
#         if not obj.alarm_time:
#             return "-"
#
#         # UTC 시간을 datetime으로 변환
#         utc_datetime = datetime.combine(datetime.today().date(), obj.alarm_time)
#
#         # timezone_offset을 적용하여 로컬 시간 계산
#         local_datetime = utc_datetime + timedelta(minutes=obj.timezone_offset)
#
#         return local_datetime.strftime("%H:%M")
#
#     alarm_local_time.short_description = "알림 시간 (로컬)"
