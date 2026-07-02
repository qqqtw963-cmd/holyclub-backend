from datetime import date
from typing import Optional

from django.db.models import Prefetch, Sum
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.bible.models import BibleBook, BibleChapter, ChapterReadLog, ReadingPlan
from app.bible.v1.reading_serializers import (
    BibleBookSerializer,
    BibleProgressMapSerializer,
    ReadingPlanProgressSerializer,
    ReadingPlanSerializer,
    ToggleReadRequestSerializer,
    ToggleReadResponseSerializer,
)
from app.common.validators import validate_view_request_user


def _clamp_percent(current: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return round(min(max((current / total) * 100, 0), 100), 1)


def _total_days_inclusive(start_date, end_date):
    return max((end_date - start_date).days + 1, 1)


def _elapsed_days(plan: ReadingPlan, today: date):
    if today < plan.start_date:
        return 0
    if today > plan.end_date:
        return _total_days_inclusive(plan.start_date, plan.end_date)
    return (today - plan.start_date).days + 1


def _recent_reading_text(read_log: Optional[ChapterReadLog]):
    if not read_log:
        return "최근 읽은 위치가 아직 없어요"
    return f"최근 읽은 위치 · {read_log.chapter.book.name_kr} {read_log.chapter.chapter_number}장"


def _average_progress_text(read_logs_qs, today: date):
    count = read_logs_qs.count()
    if count == 0:
        return "기간 평균 진도 · 아직 읽은 장이 없어요"

    first_log = read_logs_qs.order_by("read_at").first()
    if not first_log:
        return "기간 평균 진도 · 아직 읽은 장이 없어요"

    days = max((today - first_log.read_at.date()).days + 1, 1)
    average = round(count / days, 1)
    return f"기간 평균 진도 · 하루 평균 {average}장"


def _resolve_plan_for_user(user, plan_id=None):
    plans = ReadingPlan.objects.filter(user=user).order_by("-is_active", "start_date", "id")
    if plan_id:
        plan = get_object_or_404(plans, id=plan_id)
    else:
        plan = plans.filter(is_active=True).first() or plans.first()
    return plan, plans


def _get_plan_scoped_read_logs(user, plan: Optional[ReadingPlan]):
    read_logs_qs = ChapterReadLog.objects.filter(user=user)
    if plan is not None:
        read_logs_qs = read_logs_qs.filter(plan=plan)
    return read_logs_qs.select_related("chapter__book", "plan")


def _build_progress_payload(user, plan: Optional[ReadingPlan], available_plans):
    today = date.today()
    read_logs_qs = _get_plan_scoped_read_logs(user, plan)
    latest_log = read_logs_qs.order_by("-read_at", "-id").first()

    total_chapters = BibleChapter.objects.count()
    total_verses = BibleChapter.objects.aggregate(total=Sum("verse_count"))["total"] or 0
    read_chapters = read_logs_qs.count()
    read_verses = (
        BibleChapter.objects.filter(read_logs__in=read_logs_qs)
        .distinct()
        .aggregate(total=Sum("verse_count"))["total"]
        or 0
    )

    if plan:
        total_days = _total_days_inclusive(plan.start_date, plan.end_date)
        elapsed_days = _elapsed_days(plan, today)
        daily_target = round(total_chapters / total_days, 1)
        expected_by_today = round(min(daily_target * elapsed_days, total_chapters), 1)
        plan_label = f"{plan.start_date} ~ {plan.end_date}"
    else:
        total_days = 0
        elapsed_days = 0
        daily_target = 0.0
        expected_by_today = 0.0
        plan_label = "플랜이 아직 없어요"

    return {
        "plan": plan,
        "available_plans": list(available_plans),
        "recent_reading_text": _recent_reading_text(latest_log),
        "average_progress_text": _average_progress_text(read_logs_qs, today),
        "elapsed_days": {
            "current": elapsed_days,
            "total": total_days,
            "percent": _clamp_percent(elapsed_days, total_days),
            "label": f"{elapsed_days}/{total_days}" if total_days else "0/0",
            "sub_label": plan_label,
        },
        "read_chapters": {
            "current": read_chapters,
            "total": total_chapters,
            "percent": _clamp_percent(read_chapters, total_chapters),
            "label": f"{read_chapters}/{total_chapters}",
            "sub_label": f"일일 기대치 {daily_target}장",
            "daily_target": daily_target,
            "expected_by_today": expected_by_today,
        },
        "read_verses": {
            "current": read_verses,
            "total": total_verses,
            "percent": _clamp_percent(read_verses, total_verses),
            "label": f"{read_verses}/{total_verses}",
            "sub_label": "읽은 장의 절 수 합계",
        },
    }


class BibleBookListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="성경 66권/장 메타데이터 조회", responses=BibleBookSerializer(many=True))
    def get(self, request, *args, **kwargs):
        validate_view_request_user(request)
        books = BibleBook.objects.prefetch_related("chapters").order_by("order")
        serializer = BibleBookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReadingPlanListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="내 읽기 플랜 목록 조회", responses=ReadingPlanSerializer(many=True))
    def get(self, request, *args, **kwargs):
        user = validate_view_request_user(request)
        plans = ReadingPlan.objects.filter(user=user).order_by("-is_active", "start_date", "id")
        serializer = ReadingPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="읽기 플랜 생성", request=ReadingPlanSerializer, responses={201: ReadingPlanSerializer})
    def post(self, request, *args, **kwargs):
        validate_view_request_user(request)
        serializer = ReadingPlanSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()
        return Response(ReadingPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class ReadingPlanProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="읽기 플랜 진행률 조회", responses=ReadingPlanProgressSerializer)
    def get(self, request, id, *args, **kwargs):
        user = validate_view_request_user(request)
        plan = get_object_or_404(ReadingPlan, id=id, user=user)
        available_plans = ReadingPlan.objects.filter(user=user).order_by("-is_active", "start_date", "id")
        payload = _build_progress_payload(user, plan, available_plans)
        serializer = ReadingPlanProgressSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BibleProgressMapAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="책/장별 읽음 여부 전체 맵 조회", responses=BibleProgressMapSerializer)
    def get(self, request, *args, **kwargs):
        user = validate_view_request_user(request)
        raw_plan_id = request.query_params.get("plan_id")
        plan_id = int(raw_plan_id) if raw_plan_id and raw_plan_id.isdigit() else None
        plan, _plans = _resolve_plan_for_user(user, plan_id=plan_id)

        read_logs_qs = _get_plan_scoped_read_logs(user, plan)
        read_chapter_ids = set(read_logs_qs.values_list("chapter_id", flat=True))
        latest_log = read_logs_qs.order_by("-read_at", "-id").first()

        books = BibleBook.objects.prefetch_related("chapters").order_by("order")
        payload = {
            "plan_id": plan.id if plan else None,
            "recent_reading_text": _recent_reading_text(latest_log),
            "average_progress_text": _average_progress_text(read_logs_qs, date.today()),
            "books": [
                {
                    "id": book.id,
                    "book_id": book.book_id,
                    "order": book.order,
                    "name_kr": book.name_kr,
                    "name_en": book.name_en,
                    "testament": book.testament,
                    "chapter_count": book.chapter_count,
                    "chapters": [
                        {
                            "id": chapter.id,
                            "chapter_number": chapter.chapter_number,
                            "verse_count": chapter.verse_count,
                            "is_read": chapter.id in read_chapter_ids,
                        }
                        for chapter in book.chapters.all()
                    ],
                }
                for book in books
            ],
        }
        serializer = BibleProgressMapSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BibleChapterToggleReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="장 읽음 토글", request=ToggleReadRequestSerializer, responses={200: ToggleReadResponseSerializer})
    def post(self, request, id, *args, **kwargs):
        user = validate_view_request_user(request)
        serializer = ToggleReadRequestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        chapter = get_object_or_404(BibleChapter.objects.select_related("book"), id=id)

        read_log = ChapterReadLog.objects.filter(user=user, chapter=chapter).first()
        if read_log:
            read_log_id = read_log.id
            read_log.delete()
            payload = {
                "chapter_id": chapter.id,
                "is_read": False,
                "read_log_id": None,
                "recent_reading_text": "최근 읽은 위치가 아직 없어요",
            }
            latest = ChapterReadLog.objects.filter(user=user).select_related("chapter__book").order_by("-read_at", "-id").first()
            payload["recent_reading_text"] = _recent_reading_text(latest)
            return Response(ToggleReadResponseSerializer(payload).data, status=status.HTTP_200_OK)

        plan = None
        plan_id = serializer.validated_data.get("plan_id")
        if plan_id:
            plan = ReadingPlan.objects.filter(user=user, id=plan_id).first()
        if plan is None:
            plan = ReadingPlan.objects.filter(user=user, is_active=True).first()

        read_log = ChapterReadLog.objects.create(user=user, plan=plan, chapter=chapter)
        payload = {
            "chapter_id": chapter.id,
            "is_read": True,
            "read_log_id": read_log.id,
            "recent_reading_text": _recent_reading_text(read_log),
        }
        return Response(ToggleReadResponseSerializer(payload).data, status=status.HTTP_200_OK)
