import json
from pathlib import Path

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "bible_chapter_verses.json"


def seed_bible_books_and_chapters(apps, schema_editor):
    BibleBook = apps.get_model("bible", "BibleBook")
    BibleChapter = apps.get_model("bible", "BibleChapter")

    if BibleBook.objects.exists() or not DATA_FILE.exists():
        return

    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    for item in payload:
        book = BibleBook.objects.create(
            book_id=item["book_id"],
            order=item["order"],
            name_kr=item["name_kr"],
            name_en=item["name_en"],
            testament=item["testament"],
            chapter_count=item["chapter_count"],
        )
        BibleChapter.objects.bulk_create(
            [
                BibleChapter(
                    book=book,
                    chapter_number=index,
                    verse_count=verse_count,
                )
                for index, verse_count in enumerate(item["chapter_verse_counts"], start=1)
            ]
        )


def unseed_bible_books_and_chapters(apps, schema_editor):
    BibleBook = apps.get_model("bible", "BibleBook")
    BibleBook.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("bible", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BibleBook",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("book_id", models.CharField(choices=[('GENESIS', '창세기'), ('EXODUS', '출애굽기'), ('LEVITICUS', '레위기'), ('NUMBERS', '민수기'), ('DEUTERONOMY', '신명기'), ('JOSHUA', '여호수아'), ('JUDGES', '사사기'), ('RUTH', '룻기'), ('1_SAMUEL', '사무엘상'), ('2_SAMUEL', '사무엘하'), ('1_KINGS', '열왕기상'), ('2_KINGS', '열왕기하'), ('1_CHRONICLES', '역대상'), ('2_CHRONICLES', '역대하'), ('EZRA', '에스라'), ('NEHEMIAH', '느헤미야'), ('ESTHER', '에스더'), ('JOB', '욥기'), ('PSALMS', '시편'), ('PROVERBS', '잠언'), ('ECCLESIASTES', '전도서'), ('SONG_OF_SONGS', '아가'), ('ISAIAH', '이사야'), ('JEREMIAH', '예레미야'), ('LAMENTATIONS', '예레미야애가'), ('EZEKIEL', '에스겔'), ('DANIEL', '다니엘'), ('HOSEA', '호세아'), ('JOEL', '요엘'), ('AMOS', '아모스'), ('OBADIAH', '오바댜'), ('JONAH', '요나'), ('MICAH', '미가'), ('NAHUM', '나훔'), ('HABAKKUK', '하박국'), ('ZEPHANIAH', '스바냐'), ('HAGGAI', '학개'), ('ZECHARIAH', '스가랴'), ('MALACHI', '말라기'), ('MATTHEW', '마태복음'), ('MARK', '마가복음'), ('LUKE', '누가복음'), ('JOHN', '요한복음'), ('ACTS', '사도행전'), ('ROMANS', '로마서'), ('1_CORINTHIANS', '고린도전서'), ('2_CORINTHIANS', '고린도후서'), ('GALATIANS', '갈라디아서'), ('EPHESIANS', '에베소서'), ('PHILIPPIANS', '빌립보서'), ('COLOSSIANS', '골로새서'), ('1_THESSALONIANS', '데살로니가전서'), ('2_THESSALONIANS', '데살로니가후서'), ('1_TIMOTHY', '디모데전서'), ('2_TIMOTHY', '디모데후서'), ('TITUS', '디도서'), ('PHILEMON', '빌레몬서'), ('HEBREWS', '히브리서'), ('JAMES', '야고보서'), ('1_PETER', '베드로전서'), ('2_PETER', '베드로후서'), ('1_JOHN', '요한일서'), ('2_JOHN', '요한이서'), ('3_JOHN', '요한삼서'), ('JUDE', '유다서'), ('REVELATION', '요한계시록')], max_length=20, unique=True, verbose_name='권 ID')),
                ("order", models.PositiveSmallIntegerField(verbose_name="순서")),
                ("name_kr", models.CharField(max_length=20, verbose_name="한글 이름")),
                ("name_en", models.CharField(max_length=30, verbose_name="영문 이름")),
                ("testament", models.CharField(choices=[("OT", "구약"), ("NT", "신약")], max_length=2, verbose_name="구약/신약")),
                ("chapter_count", models.PositiveSmallIntegerField(verbose_name="총 장 수")),
            ],
            options={"verbose_name": "성경 권", "verbose_name_plural": "성경 권", "db_table": "bible_book", "ordering": ["order"]},
        ),
        migrations.CreateModel(
            name="ReadingPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("name", models.CharField(max_length=50, verbose_name="플랜명")),
                ("start_date", models.DateField(verbose_name="시작일")),
                ("end_date", models.DateField(verbose_name="종료일")),
                ("is_active", models.BooleanField(default=True, verbose_name="활성 여부")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reading_plans", to=settings.AUTH_USER_MODEL, verbose_name="유저")),
            ],
            options={"verbose_name": "성경 읽기 플랜", "verbose_name_plural": "성경 읽기 플랜", "db_table": "reading_plan", "ordering": ["-is_active", "start_date", "id"]},
        ),
        migrations.CreateModel(
            name="BibleChapter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("chapter_number", models.PositiveSmallIntegerField(verbose_name="장 번호")),
                ("verse_count", models.PositiveSmallIntegerField(verbose_name="절 수")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chapters", to="bible.biblebook", verbose_name="성경 권")),
            ],
            options={"verbose_name": "성경 장", "verbose_name_plural": "성경 장", "db_table": "bible_chapter", "ordering": ["book__order", "chapter_number"]},
        ),
        migrations.CreateModel(
            name="ChapterReadLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("read_at", models.DateTimeField(auto_now_add=True, verbose_name="읽은 시각")),
                ("chapter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="read_logs", to="bible.biblechapter", verbose_name="성경 장")),
                ("plan", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="read_logs", to="bible.readingplan", verbose_name="플랜")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chapter_read_logs", to=settings.AUTH_USER_MODEL, verbose_name="유저")),
            ],
            options={"verbose_name": "장 읽기 기록", "verbose_name_plural": "장 읽기 기록", "db_table": "chapter_read_log", "ordering": ["-read_at", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="biblechapter",
            constraint=models.UniqueConstraint(fields=("book", "chapter_number"), name="unique_bible_chapter_per_book"),
        ),
        migrations.AddConstraint(
            model_name="chapterreadlog",
            constraint=models.UniqueConstraint(fields=("user", "chapter"), name="unique_chapter_read_log_per_user_chapter"),
        ),
        migrations.RunPython(seed_bible_books_and_chapters, unseed_bible_books_and_chapters),
    ]
