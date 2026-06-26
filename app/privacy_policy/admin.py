from django.contrib import admin

from app.privacy_policy.models import PrivacyPolicyProxy


@admin.register(PrivacyPolicyProxy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ("version", "created_at", "updated_at")
    readonly_fields = ("version", "created_at", "updated_at")

    def get_fields(self, request, obj=None):
        if obj:  # 수정할 때
            return ("version", "content")
        else:  # 생성할 때
            return ("content",)
