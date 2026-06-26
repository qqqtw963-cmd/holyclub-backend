from django.contrib import admin

from app.verifier.models import EmailVerifier, PhoneVerifier

# @admin.register(EmailVerifier)
# class EmailVerifierAdmin(admin.ModelAdmin):
#     list_display = ["email", "code", "created_at"]
#     list_filter = ["created_at"]
#     search_fields = ["email"]
#     readonly_fields = ["created_at", "updated_at"]
#
#
# @admin.register(PhoneVerifier)
# class PhoneVerifierAdmin(admin.ModelAdmin):
#     list_display = ["phone", "code", "created_at"]
#     list_filter = ["created_at"]
#     search_fields = ["phone"]
#     readonly_fields = ["created_at", "updated_at"]
