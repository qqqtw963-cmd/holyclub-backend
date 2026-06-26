from rest_framework import status
from rest_framework.test import APITestCase

from app.screen_time.models import DailyScreenTimeLog
from app.user.models import User


class ScreenTimeAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="screen@test.com", password="test1234", name="스크린", birth_date="19900101")

    def test_upsert_screen_time(self):
        self.client.force_authenticate(self.user)
        path = "/v1/screen_time/"

        first = self.client.post(path, {"date": "2026-06-26", "minutes": 95})
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyScreenTimeLog.objects.count(), 1)

        second = self.client.post(path, {"date": "2026-06-26", "minutes": 120})
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyScreenTimeLog.objects.count(), 1)
        self.assertEqual(DailyScreenTimeLog.objects.get(user=self.user, date="2026-06-26").minutes, 120)
