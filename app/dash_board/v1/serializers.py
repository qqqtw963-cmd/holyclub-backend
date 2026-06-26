from rest_framework import serializers


class DailyResultItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="항목 ID (1-7)")
    name = serializers.CharField(help_text="항목명")
    value = serializers.IntegerField(required=False, help_text="값 (기도: 분, 말씀: 장수, 죄와의싸움: 점수)")
    practice = serializers.CharField(required=False, help_text="실천 내용")
    is_completed = serializers.BooleanField(help_text="완료 여부")


class DailyDashboardResponseSerializer(serializers.Serializer):
    date = serializers.CharField(help_text="조회 날짜 (YYYY-MM-DD)")
    results = DailyResultItemSerializer(many=True, help_text="일별 결과 목록")


class WeeklyDailyDataItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="요일 ID (1-7)")
    day = serializers.CharField(help_text="요일명")
    day_date = serializers.CharField(help_text="해당 일자 (YYYY-MM-DD)")
    value = serializers.IntegerField(required=False, help_text="값 (기도: 분, 말씀: 장수, 죄와의싸움: 점수)")
    is_completed = serializers.BooleanField(help_text="완료 여부")


class WeeklyResultItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="항목 ID (1-7)")
    name = serializers.CharField(help_text="항목명")
    average = serializers.IntegerField(required=False, help_text="주간 평균값")
    practice = serializers.CharField(required=False, help_text="실천 내용")
    daily_data = WeeklyDailyDataItemSerializer(many=True, help_text="일별 데이터 목록")


class WeeklyDashboardResponseSerializer(serializers.Serializer):
    date = serializers.CharField(help_text="조회 날짜 (YYYY-MM-DD)")
    results = WeeklyResultItemSerializer(many=True, help_text="주별 결과 목록")
