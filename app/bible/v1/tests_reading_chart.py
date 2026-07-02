from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from app.bible.models import BibleBook, BibleChapter, ChapterReadLog, ReadingPlan
from app.user.models import User


class BibleReadingChartBaseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="reader@test.com")
        self.other_user = User.objects.create_user(email="other@test.com")
        self.genesis = BibleBook.objects.get(book_id="GENESIS")
        self.matthew = BibleBook.objects.get(book_id="MATTHEW")
        self.genesis_1 = BibleChapter.objects.get(book=self.genesis, chapter_number=1)
        self.genesis_2 = BibleChapter.objects.get(book=self.genesis, chapter_number=2)
        self.matthew_1 = BibleChapter.objects.get(book=self.matthew, chapter_number=1)


class BibleBookListAPITest(BibleReadingChartBaseTestCase):
    PATH = "/v1/bible/books/"

    def test_success_response(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 66)
        self.assertEqual(response.data[0]["book_id"], "GENESIS")
        self.assertEqual(response.data[0]["chapter_count"], 50)
        self.assertEqual(response.data[0]["chapters"][0]["chapter_number"], 1)
        self.assertEqual(response.data[0]["chapters"][0]["verse_count"], 31)

    def test_failure_response_authentication_failed(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReadingPlanListCreateAPITest(BibleReadingChartBaseTestCase):
    PATH = "/v1/bible/plans/"

    def test_list_success_response(self):
        ReadingPlan.objects.create(
            user=self.user,
            name="신구약 1독",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=179),
            is_active=True,
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "신구약 1독")

    def test_create_success_response_and_deactivate_existing_active_plan(self):
        ReadingPlan.objects.create(
            user=self.user,
            name="이전 플랜",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=89),
            is_active=True,
        )
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.PATH,
            data={
                "name": "신구약 1독",
                "startDate": str(date(2026, 1, 1)),
                "endDate": str(date(2026, 6, 30)),
                "isActive": True,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "신구약 1독")
        self.assertTrue(ReadingPlan.objects.filter(user=self.user, name="신구약 1독", is_active=True).exists())
        self.assertFalse(ReadingPlan.objects.filter(user=self.user, name="이전 플랜", is_active=True).exists())


class ReadingPlanProgressAPITest(BibleReadingChartBaseTestCase):
    def setUp(self):
        super().setUp()
        self.plan = ReadingPlan.objects.create(
            user=self.user,
            name="신구약 1독",
            start_date=date.today() - timedelta(days=4),
            end_date=date.today() + timedelta(days=5),
            is_active=True,
        )
        ChapterReadLog.objects.create(user=self.user, plan=self.plan, chapter=self.genesis_1)
        ChapterReadLog.objects.create(user=self.user, plan=self.plan, chapter=self.genesis_2)

    def test_progress_success_response(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/v1/bible/plans/{self.plan.id}/progress/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["plan"]["id"], self.plan.id)
        self.assertEqual(response.data["read_chapters"]["current"], 2)
        self.assertEqual(response.data["read_verses"]["current"], self.genesis_1.verse_count + self.genesis_2.verse_count)
        self.assertEqual(response.data["elapsed_days"]["current"], 5)
        self.assertIn("최근 읽은 위치", response.data["recent_reading_text"])

    def test_progress_filters_logs_by_selected_plan(self):
        other_plan = ReadingPlan.objects.create(
            user=self.user,
            name="다른 플랜",
            start_date=date.today() - timedelta(days=2),
            end_date=date.today() + timedelta(days=30),
            is_active=False,
        )
        ChapterReadLog.objects.create(user=self.user, plan=other_plan, chapter=self.matthew_1)

        self.client.force_authenticate(self.user)
        response = self.client.get(f"/v1/bible/plans/{self.plan.id}/progress/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["read_chapters"]["current"], 2)
        self.assertEqual(
            response.data["read_verses"]["current"],
            self.genesis_1.verse_count + self.genesis_2.verse_count,
        )


class BibleProgressMapAPITest(BibleReadingChartBaseTestCase):
    PATH = "/v1/bible/progress/"

    def setUp(self):
        super().setUp()
        self.plan = ReadingPlan.objects.create(
            user=self.user,
            name="신구약 1독",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=179),
            is_active=True,
        )
        ChapterReadLog.objects.create(user=self.user, plan=self.plan, chapter=self.genesis_1)

    def test_success_response(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.PATH, data={"plan_id": self.plan.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["plan_id"], self.plan.id)
        self.assertEqual(len(response.data["books"]), 66)
        first_book = response.data["books"][0]
        self.assertEqual(first_book["book_id"], "GENESIS")
        self.assertTrue(first_book["chapters"][0]["is_read"])
        self.assertFalse(first_book["chapters"][1]["is_read"])

    def test_progress_map_filters_logs_by_selected_plan(self):
        other_plan = ReadingPlan.objects.create(
            user=self.user,
            name="신약 플랜",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=89),
            is_active=False,
        )
        ChapterReadLog.objects.create(user=self.user, plan=other_plan, chapter=self.matthew_1)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.PATH, data={"plan_id": self.plan.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genesis_book = response.data["books"][0]
        matthew_book = next(book for book in response.data["books"] if book["book_id"] == "MATTHEW")
        self.assertTrue(genesis_book["chapters"][0]["is_read"])
        self.assertFalse(matthew_book["chapters"][0]["is_read"])


class BibleChapterToggleReadAPITest(BibleReadingChartBaseTestCase):
    def setUp(self):
        super().setUp()
        self.plan = ReadingPlan.objects.create(
            user=self.user,
            name="신구약 1독",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=179),
            is_active=True,
        )

    def test_toggle_on_and_off(self):
        self.client.force_authenticate(self.user)
        path = f"/v1/bible/chapters/{self.matthew_1.id}/toggle-read/"

        create_response = self.client.post(path, data={"planId": self.plan.id})
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        self.assertTrue(create_response.data["is_read"])
        self.assertTrue(ChapterReadLog.objects.filter(user=self.user, chapter=self.matthew_1).exists())

        delete_response = self.client.post(path, data={"planId": self.plan.id})
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertFalse(delete_response.data["is_read"])
        self.assertFalse(ChapterReadLog.objects.filter(user=self.user, chapter=self.matthew_1).exists())
