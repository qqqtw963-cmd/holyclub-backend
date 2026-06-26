from collections import defaultdict
from datetime import timedelta

from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.bible_reading_log.models import BibleReadingLog
from app.common.validators import validate_view_request_user
from app.daily_check_status.models import CheckType, DailyCheckStatus
from app.groups.models import Group, GroupInvite, GroupMemberRole, GroupMembership, GroupStatus
from app.groups.v1.permissions import GroupPermission
from app.groups.v1.serializers import (
    GroupCreateResponseSerializer,
    GroupCreateSerializer,
    GroupDashboardResponseSerializer,
    GroupDetailSerializer,
    GroupInviteCreateSerializer,
    GroupJoinResponseSerializer,
    GroupJoinSerializer,
    GroupLeaveResponseSerializer,
    GroupMineSerializer,
)
from app.pray_time_log.models import PrayTimeLog
from app.screen_time.models import DailyScreenTimeLog
from app.spiritual_discipline.models import SpiritualDiscipline


@extend_schema_view(
    create=extend_schema(summary="그룹 생성 신청", responses={201: GroupCreateResponseSerializer()}),
    retrieve=extend_schema(summary="그룹 상세 조회", responses={200: GroupDetailSerializer()}),
)
class GroupViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Group.objects.select_related("leader").all()
    serializer_class = GroupCreateSerializer
    permission_classes = [GroupPermission]
    pagination_class = None
    filterset_class = None
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return GroupCreateSerializer
        if self.action == "retrieve":
            return GroupDetailSerializer
        if self.action == "mine":
            return GroupMineSerializer
        if self.action == "create_invite":
            return GroupInviteCreateSerializer
        if self.action == "join":
            return GroupJoinSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = GroupCreateResponseSerializer(instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        group = super().get_object()
        if self.action in ["retrieve", "create_invite", "leave", "dashboard"]:
            self.get_active_membership(group)
        return group

    def get_active_membership(self, group):
        request_user = validate_view_request_user(self.request)
        membership = GroupMembership.objects.filter(group=group, user=request_user, is_active=True).first()
        if not membership:
            raise PermissionDenied(detail="해당 그룹의 활성 멤버만 접근할 수 있습니다.")
        return membership

    @extend_schema(summary="내가 속한 그룹 목록", responses={200: GroupMineSerializer(many=True)})
    @action(methods=["GET"], detail=False)
    def mine(self, request):
        request_user = validate_view_request_user(request)
        memberships = GroupMembership.objects.filter(user=request_user, is_active=True).select_related("group", "group__leader")
        groups = []
        for membership in memberships:
            group = membership.group
            group.membership_role = membership.role
            groups.append(group)
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="초대 코드 생성")
    @action(methods=["POST"], detail=True, url_path="invites")
    def create_invite(self, request, pk=None):
        group = self.get_object()
        membership = self.get_active_membership(group)
        if membership.role != GroupMemberRole.LEADER:
            raise PermissionDenied(detail="그룹 리더만 초대 코드를 생성할 수 있습니다.")

        serializer = self.get_serializer(data=request.data, context={**self.get_serializer_context(), "group": group})
        serializer.is_valid(raise_exception=True)
        invite = serializer.save()
        return Response(GroupInviteCreateSerializer(invite).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="초대 코드로 그룹 가입", request=GroupJoinSerializer(), responses={200: GroupJoinResponseSerializer()})
    @action(methods=["POST"], detail=False, url_path="join")
    def join(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_user = validate_view_request_user(request)

        invite = GroupInvite.objects.select_related("group").filter(code=serializer.validated_data["code"]).first()
        if not invite:
            raise ValidationError({"code": ["유효하지 않은 초대 코드입니다."]})
        if not invite.is_valid():
            raise ValidationError({"code": ["사용할 수 없는 초대 코드입니다."]})
        if invite.group.status != GroupStatus.APPROVED:
            raise ValidationError({"code": ["승인된 그룹에만 가입할 수 있습니다."]})

        with transaction.atomic():
            membership, created = GroupMembership.objects.select_for_update().get_or_create(
                group=invite.group,
                user=request_user,
                defaults={"role": GroupMemberRole.MEMBER, "is_active": True},
            )
            if not created:
                if membership.is_active:
                    raise ValidationError({"code": ["이미 가입한 그룹입니다."]})
                membership.role = GroupMemberRole.MEMBER
                membership.is_active = True
                membership.save(update_fields=["role", "is_active"])

            invite.use_count += 1
            invite.save(update_fields=["use_count"])

        data = {
            "group_id": invite.group_id,
            "membership_id": membership.id,
            "role": membership.role,
            "status": invite.group.status,
        }
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(summary="그룹 탈퇴", responses={200: GroupLeaveResponseSerializer()})
    @action(methods=["DELETE"], detail=True, url_path="leave")
    def leave(self, request, pk=None):
        group = self.get_object()
        membership = self.get_active_membership(group)
        membership.is_active = False
        membership.save(update_fields=["is_active"])
        return Response({"group_id": group.id, "is_active": membership.is_active}, status=status.HTTP_200_OK)

    @extend_schema(summary="그룹 대시보드", responses={200: GroupDashboardResponseSerializer()})
    @action(methods=["GET"], detail=True, url_path="dashboard")
    def dashboard(self, request, pk=None):
        group = Group.objects.prefetch_related(
            Prefetch(
                "memberships",
                queryset=GroupMembership.objects.filter(is_active=True).select_related("user").order_by("joined_at"),
            )
        ).get(pk=pk)
        self.get_active_membership(group)

        memberships = list(group.memberships.all())
        member_ids = [membership.user_id for membership in memberships]
        today = timezone.localdate()
        week_start = today - timedelta(days=6)
        all_check_types = {choice for choice, _ in CheckType.choices}

        prayer_user_ids = set(
            PrayTimeLog.objects.filter(user_id__in=member_ids, recognized_date=today).values_list("user_id", flat=True).distinct()
        )
        word_user_ids = set(
            BibleReadingLog.objects.filter(user_id__in=member_ids, recognized_date=today).values_list("user_id", flat=True).distinct()
        )
        training_user_ids = set(
            SpiritualDiscipline.objects.filter(weekly_sd__user_id__in=member_ids, recognized_date=today)
            .values_list("weekly_sd__user_id", flat=True)
            .distinct()
        )

        screen_time_map = {
            item["user_id"]: item["minutes"]
            for item in DailyScreenTimeLog.objects.filter(user_id__in=member_ids, date=today).values("user_id", "minutes")
        }

        daily_checks = DailyCheckStatus.objects.filter(
            user_id__in=member_ids,
            recognized_date__range=(week_start, today),
        ).values("user_id", "recognized_date", "check_type")

        check_map = defaultdict(set)
        for item in daily_checks:
            check_map[(item["user_id"], item["recognized_date"])].add(item["check_type"])

        members = []
        for membership in memberships:
            user = membership.user
            completed_days = 0
            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)
                if check_map.get((user.id, current_date), set()) >= all_check_types:
                    completed_days += 1

            members.append(
                {
                    "user_id": user.id,
                    "name": user.name,
                    "today": {
                        "prayer_done": user.id in prayer_user_ids,
                        "word_done": user.id in word_user_ids,
                        "training_done": user.id in training_user_ids,
                        "daily_routine_done": check_map.get((user.id, today), set()) >= all_check_types,
                        "screen_time_minutes": screen_time_map.get(user.id),
                    },
                    "week_summary": {
                        "completed_days": completed_days,
                        "total_days": 7,
                    },
                    "streak": None,
                }
            )

        data = {
            "group": {"id": group.id, "name": group.name},
            "members": members,
        }
        serializer = GroupDashboardResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
