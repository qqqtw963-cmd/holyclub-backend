from django.conf import settings
from django.db import models

from app.bible.utils import BibleBookType
from app.common.models import BaseModel


class Bible(BaseModel):
    data = models.FileField(verbose_name="데이터", upload_to="bible/")

    class Meta:
        db_table = "bible"
        verbose_name = "성경"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "성경"


class BibleBook(BaseModel):
    class Testament(models.TextChoices):
        OLD = "OT", "구약"
        NEW = "NT", "신약"

    book_id = models.CharField(
        verbose_name="권 ID",
        max_length=20,
        unique=True,
        choices=BibleBookType.choices,
    )
    order = models.PositiveSmallIntegerField(verbose_name="순서")
    name_kr = models.CharField(verbose_name="한글 이름", max_length=20)
    name_en = models.CharField(verbose_name="영문 이름", max_length=30)
    testament = models.CharField(verbose_name="구약/신약", max_length=2, choices=Testament.choices)
    chapter_count = models.PositiveSmallIntegerField(verbose_name="총 장 수")

    class Meta:
        db_table = "bible_book"
        verbose_name = "성경 권"
        verbose_name_plural = verbose_name
        ordering = ["order"]

    def __str__(self):
        return self.name_kr


class BibleChapter(BaseModel):
    book = models.ForeignKey("bible.BibleBook", on_delete=models.CASCADE, related_name="chapters", verbose_name="성경 권")
    chapter_number = models.PositiveSmallIntegerField(verbose_name="장 번호")
    verse_count = models.PositiveSmallIntegerField(verbose_name="절 수")

    class Meta:
        db_table = "bible_chapter"
        verbose_name = "성경 장"
        verbose_name_plural = verbose_name
        ordering = ["book__order", "chapter_number"]
        constraints = [
            models.UniqueConstraint(fields=["book", "chapter_number"], name="unique_bible_chapter_per_book"),
        ]

    def __str__(self):
        return f"{self.book.name_kr} {self.chapter_number}장"


class BibleVerse(BaseModel):
    chapter = models.ForeignKey("bible.BibleChapter", on_delete=models.CASCADE, related_name="verses", verbose_name="성경 장")
    verse_number = models.PositiveSmallIntegerField(verbose_name="절 번호")
    translation = models.CharField(verbose_name="번역본", max_length=20, default="개역개정")
    text = models.TextField(verbose_name="본문")

    class Meta:
        db_table = "bible_verse"
        verbose_name = "성경 절"
        verbose_name_plural = verbose_name
        ordering = ["chapter__book__order", "chapter__chapter_number", "verse_number"]
        constraints = [
            models.UniqueConstraint(fields=["chapter", "verse_number", "translation"], name="unique_bible_verse_per_translation"),
        ]

    def __str__(self):
        return f"{self.chapter.book.name_kr} {self.chapter.chapter_number}:{self.verse_number}"


class BibleReference(BaseModel):
    book = models.ForeignKey("bible.BibleBook", on_delete=models.CASCADE, related_name="references", verbose_name="성경 권")
    start_chapter = models.PositiveSmallIntegerField(verbose_name="시작 장")
    start_verse = models.PositiveSmallIntegerField(verbose_name="시작 절")
    end_chapter = models.PositiveSmallIntegerField(verbose_name="끝 장")
    end_verse = models.PositiveSmallIntegerField(verbose_name="끝 절")
    translation = models.CharField(verbose_name="번역본", max_length=20, default="개역개정")

    class Meta:
        db_table = "bible_reference"
        verbose_name = "성경 구절 범위"
        verbose_name_plural = verbose_name
        ordering = ["book__order", "start_chapter", "start_verse", "end_chapter", "end_verse"]
        constraints = [
            models.UniqueConstraint(
                fields=["book", "start_chapter", "start_verse", "end_chapter", "end_verse", "translation"],
                name="unique_bible_reference_range_per_translation",
            ),
        ]

    def __str__(self):
        if self.start_chapter == self.end_chapter:
            return f"{self.book.name_kr} {self.start_chapter}:{self.start_verse}-{self.end_verse}"
        return f"{self.book.name_kr} {self.start_chapter}:{self.start_verse}-{self.end_chapter}:{self.end_verse}"


class ReadingPlan(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_plans", verbose_name="유저")
    name = models.CharField(verbose_name="플랜명", max_length=50)
    start_date = models.DateField(verbose_name="시작일")
    end_date = models.DateField(verbose_name="종료일")
    is_active = models.BooleanField(verbose_name="활성 여부", default=True)

    class Meta:
        db_table = "reading_plan"
        verbose_name = "성경 읽기 플랜"
        verbose_name_plural = verbose_name
        ordering = ["-is_active", "start_date", "id"]

    def __str__(self):
        return f"{self.user_id} - {self.name}"


class ChapterReadLog(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chapter_read_logs", verbose_name="유저")
    plan = models.ForeignKey("bible.ReadingPlan", null=True, blank=True, on_delete=models.SET_NULL, related_name="read_logs", verbose_name="플랜")
    chapter = models.ForeignKey("bible.BibleChapter", on_delete=models.CASCADE, related_name="read_logs", verbose_name="성경 장")
    read_at = models.DateTimeField(verbose_name="읽은 시각", auto_now_add=True)

    class Meta:
        db_table = "chapter_read_log"
        verbose_name = "장 읽기 기록"
        verbose_name_plural = verbose_name
        ordering = ["-read_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "chapter"], name="unique_chapter_read_log_per_user_chapter"),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.chapter}"
