from django.contrib import admin

from app.bible.models import Bible
from app.bible_version.models import BibleVersion


class BibleVersionInline(admin.TabularInline):
    model = BibleVersion
    extra = 0


@admin.register(Bible)
class BibleAdmin(admin.ModelAdmin):
    inlines = [BibleVersionInline]
    list_display = ["link", "updated_at"]

    @admin.display(description="관리")
    def link(self, obj):
        return "수정"

    def has_add_permission(self, request):
        return self.model.objects.count() == 0
