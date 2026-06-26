from datetime import datetime, timedelta

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.bible_reading_log.models import BibleReadingLog
from app.common.validators import validate_view_request_user
from app.daily_check_status.models import CheckType, DailyCheckStatus
from app.dash_board.v1.serializers import DailyDashboardResponseSerializer, WeeklyDashboardResponseSerializer
from app.mortification_of_sin.models import MortificationOfSin, WeeklyMortificationOfSin, WeeklyMortificationOfSinSlot
from app.pray_time_log.models import PrayTimeLog
from app.spiritual_discipline.models import SpiritualDiscipline, WeeklySpiritualDiscipline


class DashBoardViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="일별 집계",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="조회 날짜 (YYYY-MM-DD)",
            )
        ],
        responses={200: DailyDashboardResponseSerializer},
    )
    @action(methods=["GET"], detail=False)
    def daily(self, request):
        local_date_str = request.query_params.get("date")
        request_user = validate_view_request_user(self.request)

        if not local_date_str:
            return Response(
                {"error": "날짜 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_date = datetime.strptime(local_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. 기도 - PrayTimeLog에서 총 시간(분) 계산
        pray_logs = PrayTimeLog.objects.filter(
            user=request_user,
            recognized_date=target_date,
        )
        total_pray_seconds = sum(log.duration_seconds for log in pray_logs)
        total_pray_minutes = total_pray_seconds // 60

        # 2. 말씀 - BibleReadingLog에서 읽은 장 수 계산
        bible_reading_log = BibleReadingLog.objects.filter(
            user=request_user,
            recognized_date=target_date,
        ).first()
        bible_count = bible_reading_log.count if bible_reading_log else 0

        # 3. 예배 - DailyCheckStatus에서 WORSHIP 타입 확인
        worship_check = DailyCheckStatus.objects.filter(
            user=request_user,
            recognized_date=target_date,
            check_type=CheckType.WORSHIP,
        ).exists()

        # 4. 산상수훈 - DailyCheckStatus에서 SOM_READING_STATUS 타입 확인
        som_check = DailyCheckStatus.objects.filter(
            user=request_user,
            recognized_date=target_date,
            check_type=CheckType.SOM_READING_STATUS,
        ).exists()

        # 5-7을 위한 한 주 시작일
        target_week_start_sunday = target_date - timedelta(days=(target_date.weekday() + 1) % 7)

        # 5. 경건의 습관
        weekly_sd = WeeklySpiritualDiscipline.objects.filter(
            user=request_user,
            week_start_sunday=target_week_start_sunday,
        ).first()

        spiritual_practice = ""
        if weekly_sd:
            spiritual_practice = weekly_sd.practice

        spiritual_discipline = SpiritualDiscipline.objects.filter(
            weekly_sd__user=request_user,
            recognized_date=target_date,
        ).first()

        # 6. 죄와의 싸움 I
        weekly_mos_first = WeeklyMortificationOfSin.objects.filter(
            user=request_user,
            week_start_sunday=target_week_start_sunday,
            slot=WeeklyMortificationOfSinSlot.FIRST,
        ).first()

        mos_first_practice = ""
        if weekly_mos_first:
            mos_first_practice = weekly_mos_first.practice

        mos_first = MortificationOfSin.objects.filter(
            weekly_mos__user=request_user,
            weekly_mos__slot=WeeklyMortificationOfSinSlot.FIRST,
            recognized_date=target_date,
        ).first()

        mos_first_score = 0
        if mos_first:
            mos_first_score = mos_first.score

        # 7. 죄와의 싸움 II
        weekly_mos_second = WeeklyMortificationOfSin.objects.filter(
            user=request_user,
            week_start_sunday=target_week_start_sunday,
            slot=WeeklyMortificationOfSinSlot.SECOND,
        ).first()

        mos_second_practice = ""
        if weekly_mos_second:
            mos_second_practice = weekly_mos_second.practice

        mos_second = MortificationOfSin.objects.filter(
            weekly_mos__user=request_user,
            weekly_mos__slot=WeeklyMortificationOfSinSlot.SECOND,
            recognized_date=target_date,
        ).first()

        mos_second_score = 0
        if mos_second:
            mos_second_score = mos_second.score

        data = {
            "date": local_date_str,
            "results": [
                {
                    "id": 1,
                    "name": "기도",
                    "value": total_pray_minutes,
                    "is_completed": total_pray_minutes > 0,
                },
                {
                    "id": 2,
                    "name": "말씀",
                    "value": bible_count,
                    "is_completed": bible_count > 0,
                },
                {
                    "id": 3,
                    "name": "예배",
                    "is_completed": worship_check,
                },
                {
                    "id": 4,
                    "name": "산상수훈",
                    "is_completed": som_check,
                },
                {
                    "id": 5,
                    "name": "경건의 습관",
                    "practice": spiritual_practice,
                    "is_completed": True if spiritual_discipline else False,
                },
                {
                    "id": 6,
                    "name": "죄와의 싸움 I",
                    "practice": mos_first_practice,
                    "value": mos_first_score,
                    "is_completed": mos_first is not None,
                },
                {
                    "id": 7,
                    "name": "죄와의 싸움 II",
                    "practice": mos_second_practice,
                    "value": mos_second_score,
                    "is_completed": mos_second is not None,
                },
            ],
        }

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="주별 평균",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="조회 날짜 (YYYY-MM-DD)",
            )
        ],
        responses={200: WeeklyDashboardResponseSerializer},
    )
    @action(methods=["GET"], detail=False)
    def weekly(self, request):
        local_date_str = request.query_params.get("date")
        request_user = validate_view_request_user(self.request)

        if not local_date_str:
            return Response(
                {"error": "날짜 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_date = datetime.strptime(local_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # target_date가 속한 주의 시작일(일요일) 계산
        sunday_date = target_date - timedelta(days=(target_date.weekday() + 1) % 7)

        # 한 주의 날짜 (일요일부터 토요일까지)
        week_dates = [sunday_date + timedelta(days=i) for i in range(7)]
        day_names = ["주일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"]

        # 1. 한 주의 기도 데이터
        pray_data = []
        pray_minutes_list = []
        for i, date in enumerate(week_dates):
            pray_logs = PrayTimeLog.objects.filter(
                user=request_user,
                recognized_date=date,
            )
            total_pray_seconds = sum(log.duration_seconds for log in pray_logs)
            pray_minutes = total_pray_seconds // 60
            pray_minutes_list.append(pray_minutes)

            pray_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "value": pray_minutes,
                    "is_completed": pray_minutes > 0,
                }
            )

        active_days = sum(1 for m in pray_minutes_list if m > 0)
        pray_average = sum(pray_minutes_list) / active_days if active_days > 0 else 0

        # 2. 말씀 데이터
        bible_data = []
        bible_counts_list = []
        for i, date in enumerate(week_dates):
            bible_count = BibleReadingLog.objects.filter(
                user=request_user,
                recognized_date=date,
            ).count()
            bible_counts_list.append(bible_count)

            bible_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "value": bible_count,
                    "is_completed": bible_count > 0,
                }
            )

        active_days = sum(1 for count in bible_counts_list if count > 0)
        bible_average = sum(bible_counts_list) / active_days if active_days > 0 else 0

        # 3. 예배 데이터 수집
        worship_data = []
        for i, date in enumerate(week_dates):
            worship_check = DailyCheckStatus.objects.filter(
                user=request_user,
                recognized_date=date,
                check_type=CheckType.WORSHIP,
            ).exists()

            worship_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "is_completed": worship_check,
                }
            )

        # 4. 산상수훈 데이터 수집
        som_data = []
        for i, date in enumerate(week_dates):
            som_check = DailyCheckStatus.objects.filter(
                user=request_user,
                recognized_date=date,
                check_type=CheckType.SOM_READING_STATUS,
            ).exists()

            som_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "is_completed": som_check,
                }
            )

        # 5. 경건의 습관 데이터 수집
        weekly_sd = WeeklySpiritualDiscipline.objects.filter(
            user=request_user,
            week_start_sunday=sunday_date,
        ).first()

        spiritual_practice = ""
        if weekly_sd:
            spiritual_practice = weekly_sd.practice

        spiritual_data = []
        for i, date in enumerate(week_dates):
            spiritual_discipline = SpiritualDiscipline.objects.filter(
                weekly_sd__user=request_user,
                recognized_date=date,
            ).first()

            spiritual_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "is_completed": True if spiritual_discipline else False,
                }
            )

        # 6. 죄와의 싸움 I 데이터 수집
        weekly_mos_first = WeeklyMortificationOfSin.objects.filter(
            user=request_user,
            week_start_sunday=sunday_date,
            slot=WeeklyMortificationOfSinSlot.FIRST,
        ).first()

        mos_first_practice = ""
        if weekly_mos_first:
            mos_first_practice = weekly_mos_first.practice

        mos_first_data = []
        mos_first_scores = []
        for i, date in enumerate(week_dates):
            mos_first = MortificationOfSin.objects.filter(
                weekly_mos__user=request_user,
                weekly_mos__slot=WeeklyMortificationOfSinSlot.FIRST,
                recognized_date=date,
            ).first()

            score = mos_first.score if mos_first else 0
            mos_first_scores.append(score)

            mos_first_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "value": score,
                    "is_completed": mos_first is not None,
                }
            )

        active_days = sum(1 for score in mos_first_scores if score > 0)
        mos_first_average = sum(mos_first_scores) / active_days if active_days > 0 else 0

        # 7. 죄와의 싸움 II 데이터 수집
        weekly_mos_second = WeeklyMortificationOfSin.objects.filter(
            user=request_user,
            week_start_sunday=sunday_date,
            slot=WeeklyMortificationOfSinSlot.SECOND,
        ).first()

        mos_second_practice = ""
        if weekly_mos_second:
            mos_second_practice = weekly_mos_second.practice

        mos_second_data = []
        mos_second_scores = []
        for i, date in enumerate(week_dates):
            mos_second = MortificationOfSin.objects.filter(
                weekly_mos__user=request_user,
                weekly_mos__slot=WeeklyMortificationOfSinSlot.SECOND,
                recognized_date=date,
            ).first()

            score = mos_second.score if mos_second else 0
            mos_second_scores.append(score)

            mos_second_data.append(
                {
                    "id": i + 1,
                    "day": day_names[i],
                    "day_date": date.strftime("%Y-%m-%d"),
                    "value": score,
                    "is_completed": mos_second is not None,
                }
            )

        active_days = sum(1 for score in mos_second_scores if score > 0)
        mos_second_average = sum(mos_second_scores) / active_days if active_days > 0 else 0

        # 총 data
        data = {
            "date": target_date,
            "results": [
                {
                    "id": 1,
                    "name": "기도",
                    "average": int(pray_average),
                    "daily_data": pray_data,
                },
                {
                    "id": 2,
                    "name": "말씀",
                    "average": int(bible_average),
                    "daily_data": bible_data,
                },
                {
                    "id": 3,
                    "name": "예배",
                    "daily_data": worship_data,
                },
                {
                    "id": 4,
                    "name": "산상수훈",
                    "daily_data": som_data,
                },
                {
                    "id": 5,
                    "name": "경건의 습관",
                    "practice": spiritual_practice,
                    "daily_data": spiritual_data,
                },
                {
                    "id": 6,
                    "name": "죄와의 싸움 I",
                    "average": int(mos_first_average),
                    "practice": mos_first_practice,
                    "daily_data": mos_first_data,
                },
                {
                    "id": 7,
                    "name": "죄와의 싸움 II",
                    "average": int(mos_second_average),
                    "practice": mos_second_practice,
                    "daily_data": mos_second_data,
                },
            ],
        }

        return Response(data, status=status.HTTP_200_OK)
