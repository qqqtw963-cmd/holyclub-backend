import json
from pathlib import Path

from django.db import migrations, models
import django.db.models.deletion


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "bible_verses_sample_ko.json"


def seed_sample_bible_verses(apps, schema_editor):
    BibleBook = apps.get_model("bible", "BibleBook")
    BibleChapter = apps.get_model("bible", "BibleChapter")
    BibleVerse = apps.get_model("bible", "BibleVerse")

    if BibleVerse.objects.exists() or not DATA_FILE.exists():
        return

    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    bulk_items = []
    for book_payload in payload:
        book = BibleBook.objects.filter(order=book_payload["order"]).first()
        if not book:
            continue
        chapter_map = {
            chapter.chapter_number: chapter
            for chapter in BibleChapter.objects.filter(book=book)
        }
        for chapter_index, verses in enumerate(book_payload["chapters"], start=1):
            chapter = chapter_map.get(chapter_index)
            if not chapter:
                continue
            for verse_index, verse_text in enumerate(verses, start=1):
                bulk_items.append(
                    BibleVerse(
                        chapter=chapter,
                        verse_number=verse_index,
                        translation="개역개정",
                        text=verse_text,
                    )
                )
    if bulk_items:
        BibleVerse.objects.bulk_create(bulk_items, batch_size=500)


def unseed_sample_bible_verses(apps, schema_editor):
    BibleVerse = apps.get_model("bible", "BibleVerse")
    BibleVerse.objects.filter(translation="개역개정", chapter__book__order__in=[1, 2]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("bible", "0002_bible_reading_chart"),
    ]

    operations = [
        migrations.CreateModel(
            name="BibleReference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("start_chapter", models.PositiveSmallIntegerField(verbose_name="시작 장")),
                ("start_verse", models.PositiveSmallIntegerField(verbose_name="시작 절")),
                ("end_chapter", models.PositiveSmallIntegerField(verbose_name="끝 장")),
                ("end_verse", models.PositiveSmallIntegerField(verbose_name="끝 절")),
                ("translation", models.CharField(default="개역개정", max_length=20, verbose_name="번역본")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="references", to="bible.biblebook", verbose_name="성경 권")),
            ],
            options={"verbose_name": "성경 구절 범위", "verbose_name_plural": "성경 구절 범위", "db_table": "bible_reference", "ordering": ["book__order", "start_chapter", "start_verse", "end_chapter", "end_verse"]},
        ),
        migrations.CreateModel(
            name="BibleVerse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("verse_number", models.PositiveSmallIntegerField(verbose_name="절 번호")),
                ("translation", models.CharField(default="개역개정", max_length=20, verbose_name="번역본")),
                ("text", models.TextField(verbose_name="본문")),
                ("chapter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="verses", to="bible.biblechapter", verbose_name="성경 장")),
            ],
            options={"verbose_name": "성경 절", "verbose_name_plural": "성경 절", "db_table": "bible_verse", "ordering": ["chapter__book__order", "chapter__chapter_number", "verse_number"]},
        ),
        migrations.AddConstraint(
            model_name="biblereference",
            constraint=models.UniqueConstraint(fields=("book", "start_chapter", "start_verse", "end_chapter", "end_verse", "translation"), name="unique_bible_reference_range_per_translation"),
        ),
        migrations.AddConstraint(
            model_name="bibleverse",
            constraint=models.UniqueConstraint(fields=("chapter", "verse_number", "translation"), name="unique_bible_verse_per_translation"),
        ),
        migrations.RunPython(seed_sample_bible_verses, unseed_sample_bible_verses),
    ]
