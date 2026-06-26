from django.contrib import admin
from django_celery_results.models import GroupResult, TaskResult

# Celery Results admin 숨기기
admin.site.unregister(TaskResult)
admin.site.unregister(GroupResult)
