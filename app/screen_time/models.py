from django.conf import settings
from django.db import models


class DailyScreenTimeLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    minutes = models.IntegerField()

    class Meta:
        db_table = "daily_screen_time_log"
        verbose_name = "일별 스크린타임 기록"
        verbose_name_plural = verbose_name
        ordering = ["-date", "-id"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user_id} - {self.date} ({self.minutes}분)"
