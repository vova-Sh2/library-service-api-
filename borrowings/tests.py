from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book
from borrowings.models import Borrowing
import datetime
from unittest.mock import patch

User = get_user_model()

class BorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.ChoicesCover.HARD,
            inventory=5,
            daily_fee="1.50"
        )

    @patch("borrowings.views.create_stripe_session")
    @patch("borrowings.views.bot_message.send_message")
    def test_create_borrowing(self, mock_telegram, mock_stripe):
        """Створення позичання зменшує інвентар"""
        self.client.force_authenticate(self.user)
        payload = {
            "expected_return_date": "2026-06-10",
            "book": self.book.id
        }
        res = self.client.post("/api/borrowings/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)  # зменшився на 1

    @patch("borrowings.views.create_stripe_session")
    @patch("borrowings.views.bot_message.send_message")
    def test_create_borrowing_no_inventory(self, mock_telegram, mock_stripe):
        """Не можна позичити книгу з інвентарем 0"""
        self.book.inventory = 0
        self.book.save()
        self.client.force_authenticate(self.user)
        payload = {
            "expected_return_date": "2026-06-10",
            "book": self.book.id
        }
        res = self.client.post("/api/borrowings/", payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("borrowings.views.create_stripe_session")
    @patch("borrowings.views.bot_message.send_message")
    def test_return_borrowing(self, mock_telegram, mock_stripe):
        """Повернення книги збільшує інвентар"""
        self.client.force_authenticate(self.user)
        borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=7),
            book=self.book,
            user=self.user
        )
        self.book.inventory -= 1
        self.book.save()

        res = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 5)  # повернувся

    def test_user_sees_only_own_borrowings(self):
        """Користувач бачить тільки свої позичання"""
        other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123"
        )
        Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=7),
            book=self.book,
            user=other_user
        )
        self.client.force_authenticate(self.user)
        res = self.client.get("/api/borrowings/")
        self.assertEqual(len(res.data), 0)  # не бачить чужі