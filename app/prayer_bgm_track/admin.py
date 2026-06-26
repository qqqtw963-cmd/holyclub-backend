from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from app.prayer_bgm_track.models import PrayerBgmTrack


@admin.register(PrayerBgmTrack)
class PrayerBgmTrackAdmin(OrderedModelAdmin):
    list_display = [
        "id",
        "move_up_down_links",
        "title",
        "duration_seconds",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["title"]
    readonly_fields = [
        "duration_seconds",
        "created_at",
        "updated_at",
    ]
    list_editable = ["is_active"]
