from django.contrib import admin

from app.notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "title",
        "content",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fields = [
        "title",
        "content",
        "created_at",
        "updated_at",
    ]
