from django.contrib import admin

from app.inquiry.models import InquiryProxy


@admin.register(InquiryProxy)
class InquiryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "get_user_info",
        "title",
        "created_at",
    ]
    list_filter = [
        "created_at",
    ]
    search_fields = [
        "title",
        "content",
        "user__email",
        "user__name",
    ]
    readonly_fields = [
        "user",
        "user_name",
        "user_phone",
        "user_church_name",
        "title",
        "content",
        "created_at",
        "updated_at",
    ]
    fields = [
        "user",
        "user_name",
        "user_phone",
        "user_church_name",
        "title",
        "content",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]

    def get_user_info(self, obj):
        if obj.user:
            return f"{obj.user.name} ({obj.user.email})"
        return "탈퇴한 사용자"

    get_user_info.short_description = "사용자"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
