from django.apps import AppConfig


class PrayerBgmTrackConfig(AppConfig):
    name = "app.prayer_bgm_track"
    verbose_name = "B. 기도 BGM 관리"

    def ready(self):
        pass
