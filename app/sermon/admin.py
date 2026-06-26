from django import forms
from django.contrib import admin

from app.sermon.models import OvernightSermon, SundayPreacher, SundaySermon


class SundaySermonForm(forms.ModelForm):
    class Meta:
        model = SundaySermon
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sunday_preacher"].required = True
        self.fields["sunday_preacher"].error_messages = {"required": "주일예배 설교자를 선택해 주세요."}


class OvernightSermonForm(forms.ModelForm):
    class Meta:
        model = OvernightSermon
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["overnight_worship_type"].required = True
        self.fields["overnight_worship_type"].error_messages = {"required": "주일예배 설교자를 선택해 주세요."}


@admin.register(SundayPreacher)
class SundayPreacherAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]
    ordering = ["id"]


@admin.register(SundaySermon)
class SundaySermonAdmin(admin.ModelAdmin):
    form = SundaySermonForm
    list_display = [
        "id",
        "preached_date",
        "title",
        "sunday_preacher",
    ]
    list_filter = [
        "sunday_preacher",
        "preached_date",
    ]
    search_fields = ("title", "content")
    ordering = [
        "-preached_date",
        "-created_at",
    ]
    fields = (
        "title",
        "sunday_preacher",
        "youtube_link",
        "content",
        "preached_date",
    )


@admin.register(OvernightSermon)
class OvernightSermonAdmin(admin.ModelAdmin):
    form = OvernightSermonForm
    list_display = [
        "id",
        "preached_date",
        "title",
        "overnight_worship_type",
    ]
    list_filter = [
        "overnight_worship_type",
        "preached_date",
    ]
    search_fields = (
        "title",
        "content",
    )
    ordering = [
        "-preached_date",
        "-created_at",
    ]
    fields = (
        "title",
        "overnight_worship_type",
        "youtube_link",
        "content",
        "preached_date",
    )
