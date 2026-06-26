from django.contrib import admin

from app.sms_log.models import SmsLogProxy


@admin.register(SmsLogProxy)
class SmsLogAdmin(admin.ModelAdmin):
    pass
