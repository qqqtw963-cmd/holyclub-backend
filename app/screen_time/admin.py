from django.contrib import admin

from app.screen_time.models import DailyScreenTimeLog


@admin.register(DailyScreenTimeLog)
class DailyScreenTimeLogAdmin(admin.ModelAdmin):
    list_display = ["user", "date", "minutes"]
    list_filter = ["date"]
    search_fields = ["user__name", "user__email"]
