from rest_framework import serializers

from app.bible.models import BibleBook, BibleChapter, ChapterReadLog, ReadingPlan
from app.common.validators import validate_serializer_request_user


class BibleChapterSerializer(serializers.ModelSerializer):
    chapter_number = serializers.IntegerField()
    verse_count = serializers.IntegerField()

    class Meta:
        model = BibleChapter
        fields = ["id", "chapter_number", "verse_count"]


class BibleBookSerializer(serializers.ModelSerializer):
    chapter_count = serializers.IntegerField()
    chapters = BibleChapterSerializer(many=True)

    class Meta:
        model = BibleBook
        fields = [
            "id",
            "book_id",
            "order",
            "name_kr",
            "name_en",
            "testament",
            "chapter_count",
            "chapters",
        ]


class ReadingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingPlan
        fields = ["id", "name", "start_date", "end_date", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end_date = attrs.get("end_date") or getattr(self.instance, "end_date", None)
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일보다 빠를 수 없습니다."]})
        return attrs

    def create(self, validated_data):
        request_user = validate_serializer_request_user(self, validated_data)
        is_active = validated_data.get("is_active", True)
        if is_active:
            ReadingPlan.objects.filter(user=request_user, is_active=True).update(is_active=False)
        return ReadingPlan.objects.create(user=request_user, **validated_data)


class PlanChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingPlan
        fields = ["id", "name", "start_date", "end_date", "is_active"]


class ProgressMetricSerializer(serializers.Serializer):
    current = serializers.IntegerField()
    total = serializers.IntegerField()
    percent = serializers.FloatField()
    label = serializers.CharField()
    sub_label = serializers.CharField(required=False, allow_blank=True)
    daily_target = serializers.FloatField(required=False)
    expected_by_today = serializers.FloatField(required=False)


class ReadingPlanProgressSerializer(serializers.Serializer):
    plan = PlanChoiceSerializer(allow_null=True)
    available_plans = PlanChoiceSerializer(many=True)
    recent_reading_text = serializers.CharField()
    average_progress_text = serializers.CharField()
    elapsed_days = ProgressMetricSerializer()
    read_chapters = ProgressMetricSerializer()
    read_verses = ProgressMetricSerializer()


class ChapterProgressItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    chapter_number = serializers.IntegerField()
    verse_count = serializers.IntegerField()
    is_read = serializers.BooleanField()


class BookProgressItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    book_id = serializers.CharField()
    order = serializers.IntegerField()
    name_kr = serializers.CharField()
    name_en = serializers.CharField()
    testament = serializers.CharField()
    chapter_count = serializers.IntegerField()
    chapters = ChapterProgressItemSerializer(many=True)


class BibleProgressMapSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(allow_null=True)
    recent_reading_text = serializers.CharField()
    average_progress_text = serializers.CharField()
    books = BookProgressItemSerializer(many=True)


class ToggleReadResponseSerializer(serializers.Serializer):
    chapter_id = serializers.IntegerField()
    is_read = serializers.BooleanField()
    read_log_id = serializers.IntegerField(allow_null=True)
    recent_reading_text = serializers.CharField()


class ToggleReadRequestSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_plan_id(self, value):
        if value is None:
            return value
        request_user = validate_serializer_request_user(self, {})
        if not ReadingPlan.objects.filter(id=value, user=request_user).exists():
            raise serializers.ValidationError("선택한 읽기 플랜을 찾을 수 없습니다.")
        return value
