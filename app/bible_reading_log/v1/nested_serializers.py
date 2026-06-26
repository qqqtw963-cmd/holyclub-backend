from rest_framework import serializers


class BibleReadingLogItemSerializer(serializers.Serializer):
    """성경 읽기 기록 아이템"""

    id = serializers.IntegerField(help_text="기록 ID")
    count = serializers.IntegerField(help_text="읽은 양")
    local_date = serializers.DateField(help_text="로컬 날짜")
    recognized_date = serializers.DateField(help_text="인식 날짜")
    created_at = serializers.DateTimeField(help_text="생성 시간")


class BibleReadingLogBookSerializer(serializers.Serializer):
    """성경 읽기 기록 목록"""

    logs = BibleReadingLogItemSerializer(many=True, help_text="읽기 기록들의 목록")
