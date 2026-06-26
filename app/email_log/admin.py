from django.contrib import admin

from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "recipient",
        "purpose",
        "status",
        "fail_reason",
    ]
    list_filter = [
        "purpose",
        "status",
    ]
