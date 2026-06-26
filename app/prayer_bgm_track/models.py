from django.db import models
from mutagen import File as MutagenFile
from ordered_model.models import OrderedModel

from app.common.models import BaseModel


class PrayerBgmTrack(BaseModel, OrderedModel):
    title = models.CharField(max_length=100, verbose_name="BGM 제목")
    audio_file = models.FileField(upload_to="prayer_bgm/audio/", verbose_name="음원 파일")
    thumbnail_image = models.ImageField(
        upload_to="prayer_bgm/thumbnail/",
        verbose_name="썸네일 이미지",
        null=True,
        blank=True,
    )
    duration_seconds = models.PositiveIntegerField(
        verbose_name="총 재생 시간(초)",
        help_text="진행바 표시용",
    )  # admin 에서 파일 저장할 때, 기간 체크해서 저장하도록

    is_active = models.BooleanField(
        verbose_name="활성화 여부",
        default=True,
    )

    class Meta:
        db_table = "prayer_bgm_track"
        verbose_name = "기도용 BGM"
        verbose_name_plural = verbose_name
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 새로 업로드되거나 파일이 변경된 경우에만 duration 추출
        if self.audio_file:
            try:
                # 파일 경로를 통해 메타데이터 읽기
                audio = MutagenFile(self.audio_file.path if self.pk else self.audio_file.file)
                if audio and audio.info:
                    self.duration_seconds = int(audio.info.length)
            except Exception as e:
                # 에러 발생 시 로깅하고 계속 진행
                print(f"음원 길이 추출 실패: {e}")
                pass

        super().save(*args, **kwargs)


class PrayerBgmListeningState(BaseModel):
    user = models.ForeignKey(
        "user.User",
        verbose_name="유저",
        on_delete=models.CASCADE,
    )
    track = models.ForeignKey(
        "prayer_bgm_track.PrayerBgmTrack",
        verbose_name="기도용 BGM",
        on_delete=models.CASCADE,
    )

    last_position_seconds = models.PositiveIntegerField(
        verbose_name="마지막 재생 위치(초)",
        default=0,
    )

    class Meta:
        db_table = "prayer_bgm_listening_state"
        verbose_name = "유저별 기도 BGM 재생 상태"
        verbose_name_plural = verbose_name
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "track"],
                name="prayer_bgm_listening_state_user_track_unique",
            )
        ]
