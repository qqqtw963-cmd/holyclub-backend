from django.contrib import admin

from app.spiritual_discipline.models import SpiritualDiscipline, WeeklySpiritualDiscipline

# @admin.register(WeeklySpiritualDiscipline)
# class WeeklySpiritualDisciplineAdmin(admin.ModelAdmin):
#     list_display = ["user", "practice", "week_start_sunday", "created_at"]
#     list_filter = ["week_start_sunday", "created_at"]
#     search_fields = ["user__email", "practice"]
#     readonly_fields = ["created_at", "updated_at"]
#
#
# @admin.register(SpiritualDiscipline)
# class SpiritualDisciplineAdmin(admin.ModelAdmin):
#     list_display = ["weekly_sd", "check_date", "is_checked", "created_at"]
#     list_filter = ["is_checked", "check_date", "created_at"]
#     search_fields = ["weekly_sd__practice", "weekly_sd__user__email"]
#     readonly_fields = ["created_at", "updated_at"]
