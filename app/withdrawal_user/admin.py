from django.contrib import admin

from app.withdrawal_user.models import WithdrawalUserProxy


@admin.register(WithdrawalUserProxy)
class WithdrawalUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "email",
        "name",
        "phone",
        "church_name",
        "user_created_at",
        "deleted_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
