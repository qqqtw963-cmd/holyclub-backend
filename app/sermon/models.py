from django.db import models

from app.common.models import BaseModel


class WorshipType(models.TextChoices):
    SUNDAY = "sunday", "주일"
    OVERNIGHT = "overnight", "철야"


class SundayPreacher(models.Model):
    name = models.CharField(
        verbose_name="설교자",
        unique=True,
        max_length=100,
        help_text="이름, 직책 포함해서 입력해 주세요.",
    )

    class Meta:
        db_table = "sunday_preacher"
        verbose_name = "0. 주일예배 설교자"
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class OvernightWorshipType(models.TextChoices):
    FRIDAY_NIGHT = "friday_night", "금요집회"
    THURSDAY_NIGHT = "thursday_night", "목요집회"


class Sermon(BaseModel):
    worship_type = models.CharField(
        verbose_name="예배 종류",
        choices=WorshipType.choices,
        max_length=10,
        default=WorshipType.SUNDAY,
    )  # not null

    # common
    youtube_link = models.URLField(verbose_name="유튜브 링크")
    title = models.CharField(verbose_name="제목", max_length=128)
    content = models.TextField(verbose_name="내용")
    preached_date = models.DateField(verbose_name="설교일자")

    # sunday
    sunday_preacher = models.ForeignKey(
        "sermon.SundayPreacher",
        verbose_name="주일예배 설교자",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    # overnight
    overnight_worship_type = models.CharField(
        verbose_name="철야예배 종류",
        max_length=40,
        choices=OvernightWorshipType.choices,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "sermon"
        verbose_name = "설교"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]


class SermonWatch(BaseModel):
    # 유저-설교: 중간테이블
    user = models.ForeignKey(
        "user.User",
        verbose_name="사용자",
        on_delete=models.CASCADE,
    )
    sermon = models.ForeignKey(
        "sermon.Sermon",
        verbose_name="설교",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "sermon_watch"
        verbose_name = "설교 시청 여부"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "sermon"],
                name="unique_user_sermon_watch",
            )
        ]

    # 유저와 설교 둘의 중간테이블 만들기


class SermonBookmark(BaseModel):
    # 유저-설교: 중간테이블
    user = models.ForeignKey(
        "user.User",
        verbose_name="사용자",
        on_delete=models.CASCADE,
    )
    sermon = models.ForeignKey(
        "sermon.Sermon",
        verbose_name="설교",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "sermon_bookmark"
        verbose_name = "설교 북마크"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "sermon"],
                name="unique_user_sermon_bookmark",
            )
        ]


# ----------------


class SundaySermonManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                worship_type=WorshipType.SUNDAY,
                sunday_preacher__isnull=False,
            )
        )


class OvernightSermonManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                worship_type=WorshipType.OVERNIGHT,
                overnight_worship_type__isnull=False,
            )
        )


class SundaySermon(Sermon):
    objects = SundaySermonManager()

    class Meta:
        proxy = True
        verbose_name = "1. 주일예배 설교"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.worship_type = WorshipType.SUNDAY
        super().save(*args, **kwargs)


class OvernightSermon(Sermon):
    objects = OvernightSermonManager()

    class Meta:
        proxy = True
        verbose_name = "2. 철야예배 설교"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.worship_type = WorshipType.OVERNIGHT
        super().save(*args, **kwargs)
