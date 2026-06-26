from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.daily_check_status.models import CheckType, DailyCheckStatus
from app.groups.models import Group, GroupInvite, GroupMemberRole, GroupMembership, GroupStatus
from app.pray_time_log.models import PrayTimeLog, PrayType
from app.bible_reading_log.models import BibleReadingLog
from app.screen_time.models import DailyScreenTimeLog
from app.spiritual_discipline.models import SpiritualDiscipline, WeeklySpiritualDiscipline
from app.user.models import User


class GroupAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="leader@test.com", password="test1234", name="리더", birth_date="19900101")
        self.member = User.objects.create_user(email="member@test.com", password="test1234", name="멤버", birth_date="19920101")
        self.other = User.objects.create_user(email="other@test.com", password="test1234", name="외부인", birth_date="19930101")

    def test_create_group_pending(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/v1/groups/", {"name": "다락방 1조", "description": "소개"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertListEqual(sorted(response.data.keys()), ["id", "status"])
        group = Group.objects.get(id=response.data["id"])
        self.assertEqual(group.status, GroupStatus.PENDING)
        self.assertFalse(GroupMembership.objects.filter(group=group, user=self.user).exists())

    def test_join_leave_and_dashboard_permissions(self):
        today = timezone.localdate()
        group = Group.objects.create(name="승인 그룹", description="", leader=self.user, status=GroupStatus.APPROVED, approved_at=timezone.now())
        GroupMembership.objects.create(group=group, user=self.user, role=GroupMemberRole.LEADER, is_active=True)

        weekly_sd = WeeklySpiritualDiscipline.objects.create(user=self.member, practice="훈련", week_start_sunday=today - timedelta(days=(today.weekday() + 1) % 7))
        SpiritualDiscipline.objects.create(weekly_sd=weekly_sd, recognized_date=today, local_date=today, timezone_offset=540)
        PrayTimeLog.objects.create(user=self.member, type=PrayType.MANUAL, created_at=timezone.now(), timezone_offset=540, local_date=today, recognized_date=today, duration_seconds=600)
        BibleReadingLog.objects.create(user=self.member, count=1, created_at=timezone.now(), timezone_offset=540, local_date=today, recognized_date=today)
        DailyCheckStatus.objects.create(user=self.member, check_type=CheckType.WORSHIP, created_at=timezone.now(), timezone_offset=540, local_date=today, recognized_date=today)
        DailyCheckStatus.objects.create(user=self.member, check_type=CheckType.SOM_READING_STATUS, created_at=timezone.now(), timezone_offset=540, local_date=today, recognized_date=today)
        DailyScreenTimeLog.objects.create(user=self.member, date=today, minutes=95)

        invite = GroupInvite.objects.create(group=group, code="ABCDEFGH", created_by=self.user)

        self.client.force_authenticate(self.member)
        join_response = self.client.post("/v1/groups/join/", {"code": invite.code})
        self.assertEqual(join_response.status_code, status.HTTP_200_OK)

        dashboard_response = self.client.get(f"/v1/groups/{group.id}/dashboard/")
        self.assertEqual(dashboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(dashboard_response.data["group"]["id"], group.id)
        member_row = next(item for item in dashboard_response.data["members"] if item["user_id"] == self.member.id)
        self.assertTrue(member_row["today"]["prayer_done"])
        self.assertTrue(member_row["today"]["word_done"])
        self.assertTrue(member_row["today"]["training_done"])
        self.assertTrue(member_row["today"]["daily_routine_done"])
        self.assertEqual(member_row["today"]["screen_time_minutes"], 95)

        leave_response = self.client.delete(f"/v1/groups/{group.id}/leave/")
        self.assertEqual(leave_response.status_code, status.HTTP_200_OK)
        self.assertFalse(GroupMembership.objects.get(group=group, user=self.member).is_active)

        self.client.force_authenticate(self.other)
        forbidden_response = self.client.get(f"/v1/groups/{group.id}/")
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)
