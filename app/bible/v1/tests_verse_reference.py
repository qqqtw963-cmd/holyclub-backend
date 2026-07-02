from rest_framework import status
from rest_framework.test import APITestCase

from app.bible.models import BibleBook, BibleChapter
from app.user.models import User


class BibleVerseRangeRetrieveAPITest(APITestCase):
    PATH = "/v1/bible/verses/"

    def setUp(self):
        self.user = User.objects.create_user(email="reader@test.com")
        self.book = BibleBook.objects.get(book_id="EXODUS")
        self.chapter = BibleChapter.objects.get(book=self.book, chapter_number=4)

    def test_success_response_returns_selected_range(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            self.PATH,
            data={
                "book": self.book.id,
                "start_chapter": 4,
                "start_verse": 4,
                "end_chapter": 4,
                "end_verse": 5,
                "translation": "개역개정",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reference_text"], "출애굽기 4:4-5")
        self.assertEqual(response.data["translation"], "개역개정")
        self.assertEqual(len(response.data["verses"]), 2)
        self.assertEqual(response.data["verses"][0]["verse_number"], 4)
        self.assertTrue(response.data["verses"][0]["text"])

    def test_failure_response_when_end_precedes_start(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            self.PATH,
            data={
                "book": self.book.id,
                "start_chapter": 4,
                "start_verse": 5,
                "end_chapter": 4,
                "end_verse": 4,
                "translation": "개역개정",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field", response.data)

    def test_failure_response_authentication_failed(self):
        response = self.client.get(
            self.PATH,
            data={
                "book": self.book.id,
                "start_chapter": 4,
                "start_verse": 4,
                "end_chapter": 4,
                "end_verse": 5,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
