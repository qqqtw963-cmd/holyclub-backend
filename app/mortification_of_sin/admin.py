# from django.contrib import admin
#
# from app.mortification_of_sin.models import MortificationOfSin, WeeklyMortificationOfSin
#
#
# @admin.register(WeeklyMortificationOfSin)
# class WeeklyMortificationOfSinAdmin(admin.ModelAdmin):
#     list_display = ["user", "practice", "week_start_sunday", "created_at"]
#     list_filter = ["week_start_sunday", "created_at"]
#     search_fields = ["user__email", "practice"]
#     readonly_fields = ["created_at", "updated_at"]
#
#
# @admin.register(MortificationOfSin)
# class MortificationOfSinAdmin(admin.ModelAdmin):
#     list_display = ["weekly_sd", "check_date", "score", "created_at"]
#     list_filter = ["score", "check_date", "created_at"]
#     search_fields = ["weekly_sd__practice", "weekly_sd__user__email"]
#     readonly_fields = ["created_at", "updated_at"]
