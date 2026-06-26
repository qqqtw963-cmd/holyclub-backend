from django.contrib import admin
from django.utils import timezone

from app.groups.models import Group, GroupInvite, GroupMemberRole, GroupMembership, GroupStatus


@admin.action(description="선택한 그룹 승인")
def approve_groups(modeladmin, request, queryset):
    now = timezone.now()
    for group in queryset:
        group.status = GroupStatus.APPROVED
        group.approved_at = now
        group.save(update_fields=["status", "approved_at"])
        GroupMembership.objects.update_or_create(
            group=group,
            user=group.leader,
            defaults={"role": GroupMemberRole.LEADER, "is_active": True},
        )


@admin.action(description="선택한 그룹 거절")
def reject_groups(modeladmin, request, queryset):
    queryset.update(status=GroupStatus.REJECTED, approved_at=None)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "leader", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "leader__name", "leader__email"]
    actions = [approve_groups, reject_groups]
    readonly_fields = ["created_at", "approved_at"]


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ["group", "user", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["group__name", "user__name", "user__email"]
    readonly_fields = ["joined_at"]


@admin.register(GroupInvite)
class GroupInviteAdmin(admin.ModelAdmin):
    list_display = ["group", "code", "created_by", "created_at", "expires_at", "max_uses", "use_count"]
    list_filter = ["created_at", "expires_at"]
    search_fields = ["group__name", "code", "created_by__name", "created_by__email"]
    readonly_fields = ["created_at", "use_count"]
