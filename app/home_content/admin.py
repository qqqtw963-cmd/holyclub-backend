from django.contrib import admin

from app.home_content.models import HomeContent


@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "main_title",
        "is_active",
        "updated_at",
        "created_at",
    ]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ["main_title", "sub_title", "highlight_text"]
    readonly_fields = ["created_at", "updated_at"]
    fields = [
        "eyebrow",
        "main_title",
        "sub_title",
        "highlight_text",
        "cta_text",
        "cta_link",
        "is_active",
        "created_at",
        "updated_at",
    ]
