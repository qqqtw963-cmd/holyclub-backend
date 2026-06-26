from django.contrib import admin

from app.push_log.models import PushLogProxy


@admin.register(PushLogProxy)
class PushLogAdmin(admin.ModelAdmin):
    pass
