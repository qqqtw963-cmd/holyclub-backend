from django.contrib import admin

from app.bible.models import (
    Bible,
    BibleBook,
    BibleChapter,
    BibleReference,
    BibleVerse,
    ChapterReadLog,
    ReadingPlan,
)
from app.bible_version.models import BibleVersion


class BibleVersionInline(admin.TabularInline):
    model = BibleVersion
    extra = 0


class BibleChapterInline(admin.TabularInline):
    model = BibleChapter
    extra = 0
    ordering = ("chapter_number",)
    fields = ("chapter_number", "verse_count", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Bible)
class BibleAdmin(admin.ModelAdmin):
    inlines = [BibleVersionInline]
    list_display = ["link", "updated_at"]

    @admin.display(description="관리")
    def link(self, obj):
        return "수정"

    def has_add_permission(self, request):
        return self.model.objects.count() == 0


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ("order", "name_kr", "name_en", "book_id", "testament", "chapter_count")
    list_filter = ("testament",)
    search_fields = ("name_kr", "name_en", "book_id")
    ordering = ("order",)
    inlines = [BibleChapterInline]


@admin.register(BibleChapter)
class BibleChapterAdmin(admin.ModelAdmin):
    list_display = ("book", "chapter_number", "verse_count")
    list_filter = ("book__testament", "book")
    search_fields = ("book__name_kr", "book__name_en", "book__book_id")
    ordering = ("book__order", "chapter_number")


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ("chapter", "verse_number", "translation")
    list_filter = ("translation", "chapter__book")
    search_fields = ("chapter__book__name_kr", "chapter__book__name_en", "text")
    ordering = ("chapter__book__order", "chapter__chapter_number", "verse_number")


@admin.register(BibleReference)
class BibleReferenceAdmin(admin.ModelAdmin):
    list_display = ("book", "start_chapter", "start_verse", "end_chapter", "end_verse", "translation")
    list_filter = ("translation", "book__testament")
    search_fields = ("book__name_kr", "book__name_en", "book__book_id")
    ordering = ("book__order", "start_chapter", "start_verse")


@admin.register(ReadingPlan)
class ReadingPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "start_date", "end_date", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__email", "name")
    ordering = ("-is_active", "start_date", "id")


@admin.register(ChapterReadLog)
class ChapterReadLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "chapter", "plan", "read_at")
    list_filter = ("plan", "chapter__book", "chapter__book__testament")
    search_fields = ("user__email", "chapter__book__name_kr", "chapter__book__name_en")
    ordering = ("-read_at", "-id")
