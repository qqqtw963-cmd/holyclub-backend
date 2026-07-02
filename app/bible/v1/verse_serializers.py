from rest_framework import serializers

from app.bible.models import BibleBook, BibleChapter, BibleReference, BibleVerse


class BibleVerseRangeMixin:
    default_error_messages = {
        "invalid_range": "끝 구절은 시작 구절보다 앞설 수 없어요.",
        "invalid_chapter": "선택한 장이 존재하지 않아요.",
        "invalid_verse": "선택한 절이 존재하지 않아요.",
        "empty_range": "선택한 구간의 본문 데이터가 아직 없어요.",
    }

    def _resolve_chapter(self, book: BibleBook, chapter_number: int):
        chapter = BibleChapter.objects.filter(book=book, chapter_number=chapter_number).first()
        if not chapter:
            raise serializers.ValidationError({"non_field": [self.default_error_messages["invalid_chapter"]]})
        return chapter

    def _validate_verse_number(self, chapter: BibleChapter, verse_number: int):
        if verse_number < 1 or verse_number > chapter.verse_count:
            raise serializers.ValidationError({"non_field": [self.default_error_messages["invalid_verse"]]})

    def validate(self, attrs):
        attrs = super().validate(attrs)
        book = attrs["book"]
        start_chapter = self._resolve_chapter(book, attrs["start_chapter"])
        end_chapter = self._resolve_chapter(book, attrs["end_chapter"])
        self._validate_verse_number(start_chapter, attrs["start_verse"])
        self._validate_verse_number(end_chapter, attrs["end_verse"])

        start_key = (attrs["start_chapter"], attrs["start_verse"])
        end_key = (attrs["end_chapter"], attrs["end_verse"])
        if end_key < start_key:
            raise serializers.ValidationError({"non_field": [self.default_error_messages["invalid_range"]]})

        attrs["_start_chapter_obj"] = start_chapter
        attrs["_end_chapter_obj"] = end_chapter
        return attrs


class BibleVerseRangeQuerySerializer(BibleVerseRangeMixin, serializers.Serializer):
    book = serializers.PrimaryKeyRelatedField(queryset=BibleBook.objects.all())
    start_chapter = serializers.IntegerField(min_value=1)
    start_verse = serializers.IntegerField(min_value=1)
    end_chapter = serializers.IntegerField(min_value=1)
    end_verse = serializers.IntegerField(min_value=1)
    translation = serializers.CharField(max_length=20, required=False, default="개역개정")


class BibleReferenceSerializer(BibleVerseRangeMixin, serializers.ModelSerializer):
    class Meta:
        model = BibleReference
        fields = [
            "id",
            "book",
            "start_chapter",
            "start_verse",
            "end_chapter",
            "end_verse",
            "translation",
        ]


class BibleVerseLineSerializer(serializers.ModelSerializer):
    chapter_number = serializers.IntegerField(source="chapter.chapter_number", read_only=True)

    class Meta:
        model = BibleVerse
        fields = ["chapter_number", "verse_number", "text"]


class BibleReferenceDetailSerializer(serializers.ModelSerializer):
    book_id = serializers.CharField(source="book.book_id", read_only=True)
    book_name_kr = serializers.CharField(source="book.name_kr", read_only=True)
    reference_text = serializers.SerializerMethodField()
    content_text = serializers.SerializerMethodField()
    verses = serializers.SerializerMethodField()

    class Meta:
        model = BibleReference
        fields = [
            "id",
            "book",
            "book_id",
            "book_name_kr",
            "start_chapter",
            "start_verse",
            "end_chapter",
            "end_verse",
            "translation",
            "reference_text",
            "content_text",
            "verses",
        ]

    def get_reference_text(self, obj: BibleReference):
        if obj.start_chapter == obj.end_chapter:
            if obj.start_verse == obj.end_verse:
                return f"{obj.book.name_kr} {obj.start_chapter}:{obj.start_verse}"
            return f"{obj.book.name_kr} {obj.start_chapter}:{obj.start_verse}-{obj.end_verse}"
        return f"{obj.book.name_kr} {obj.start_chapter}:{obj.start_verse}-{obj.end_chapter}:{obj.end_verse}"

    def _get_verses(self, obj: BibleReference):
        queryset = BibleVerse.objects.filter(
            chapter__book=obj.book,
            translation=obj.translation,
            chapter__chapter_number__gte=obj.start_chapter,
            chapter__chapter_number__lte=obj.end_chapter,
        ).select_related("chapter", "chapter__book").order_by("chapter__chapter_number", "verse_number")

        lines = []
        for verse in queryset:
            current_key = (verse.chapter.chapter_number, verse.verse_number)
            start_key = (obj.start_chapter, obj.start_verse)
            end_key = (obj.end_chapter, obj.end_verse)
            if start_key <= current_key <= end_key:
                lines.append(verse)
        return lines

    def get_content_text(self, obj: BibleReference):
        return " ".join(verse.text.strip() for verse in self._get_verses(obj)).strip()

    def get_verses(self, obj: BibleReference):
        return BibleVerseLineSerializer(self._get_verses(obj), many=True).data
