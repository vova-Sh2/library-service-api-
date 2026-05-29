from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book

User = get_user_model()

class BookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.ChoicesCover.HARD,
            inventory=5,
            daily_fee="1.50"
        )

    def test_list_books_unauthorized(self):
        res = self.client.get("/api/books/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "Hard",
            "inventory": 3,
            "daily_fee": "2.00"
        }
        res = self.client.post("/api/books/", payload)
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_book_unauthorized(self):
        self.client.force_authenticate(self.user)
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "Hard",
            "inventory": 3,
            "daily_fee": "2.00"
        }
        res = self.client.post("/api/books/", payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_admin(self):
        self.client.force_authenticate(self.admin)
        res = self.client.delete(f"/api/books/{self.book.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)