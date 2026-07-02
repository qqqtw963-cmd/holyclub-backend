from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.bible.models import BibleReference, BibleVerse
from app.bible.v1.verse_serializers import (
    BibleReferenceDetailSerializer,
    BibleVerseRangeQuerySerializer,
)
from app.common.validators import validate_view_request_user


class BibleVerseRangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="선택한 성경 구간 본문 조회", responses={200: BibleReferenceDetailSerializer})
    def get(self, request, *args, **kwargs):
        validate_view_request_user(request)
        serializer = BibleVerseRangeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        reference, _created = BibleReference.objects.get_or_create(
            book=data["book"],
            start_chapter=data["start_chapter"],
            start_verse=data["start_verse"],
            end_chapter=data["end_chapter"],
            end_verse=data["end_verse"],
            translation=data.get("translation") or "개역개정",
        )

        if not BibleVerse.objects.filter(
            chapter__book=reference.book,
            translation=reference.translation,
            chapter__chapter_number__gte=reference.start_chapter,
            chapter__chapter_number__lte=reference.end_chapter,
        ).exists():
            return Response({"non_field": ["선택한 구간의 본문 데이터가 아직 없어요."]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(BibleReferenceDetailSerializer(reference).data, status=status.HTTP_200_OK)
