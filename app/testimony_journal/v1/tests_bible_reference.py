from rest_framework import status
from rest_framework.test import APITestCase

from app.bible.models import BibleBook, BibleReference
from app.testimony_journal.models import TestimonyJournal
from app.user.models import User


class TestimonyJournalBibleReferenceAPITest(APITestCase):
    PATH = "/v1/testimony_journal/"

    def setUp(self):
        self.user = User.objects.create_user(email="note@test.com")
        self.book = BibleBook.objects.get(book_id="EXODUS")

    def test_create_and_retrieve_with_bible_reference(self):
        self.client.force_authenticate(self.user)
        create_response = self.client.post(
            self.PATH,
            data={
                "content": "본문입니다.",
                "bibleReference": {
                    "book": self.book.id,
                    "startChapter": 4,
                    "startVerse": 4,
                    "endChapter": 4,
                    "endVerse": 5,
                    "translation": "개역개정",
                },
            },
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["bible_reference"]["reference_text"], "출애굽기 4:4-5")
        self.assertTrue(BibleReference.objects.filter(book=self.book, start_chapter=4, start_verse=4, end_chapter=4, end_verse=5).exists())

        retrieve_response = self.client.get(f"{self.PATH}{create_response.data['id']}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["bible_reference"]["translation"], "개역개정")

    def test_update_allows_clearing_bible_reference(self):
        self.client.force_authenticate(self.user)
        reference = BibleReference.objects.create(
            book=self.book,
            start_chapter=4,
            start_verse=4,
            end_chapter=4,
            end_verse=5,
            translation="개역개정",
        )
        journal = TestimonyJournal.objects.create(user=self.user, content="기존", bible_reference=reference)

        response = self.client.put(
            f"{self.PATH}{journal.id}/",
            data={
                "content": "수정됨",
                "bibleReference": None,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        journal.refresh_from_db()
        self.assertIsNone(journal.bible_reference)

    def test_create_rejects_invalid_reference_range(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.PATH,
            data={
                "content": "본문입니다.",
                "bibleReference": {
                    "book": self.book.id,
                    "startChapter": 4,
                    "startVerse": 5,
                    "endChapter": 4,
                    "endVerse": 4,
                    "translation": "개역개정",
                },
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("bible_reference", response.data)
        self.assertIn("non_field", response.data["bible_reference"])
