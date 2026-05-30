from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import datetime
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()

PAYMENTS_URL = "/api/payments/"


def detail_url(payment_id):
    return f"/api/payments/{payment_id}/"


def create_payment(borrowing, **params):
    defaults = {
        "status": Payment.StausChoices.PENDING,
        "type": Payment.TypeChoices.PAYMENT,
        "borrowing": borrowing,
        "session_url": "https://checkout.stripe.com/test",
        "session_id": "cs_test_123",
        "money_to_pay": "14.00",
    }
    defaults.update(params)
    return Payment.objects.create(**defaults)


class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="testpass123"
        )
        self.user = User.objects.create_user(
            email="user@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.ChoicesCover.HARD,
            inventory=5,
            daily_fee="2.00",
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        self.other_borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=5),
            book=self.book,
            user=self.other_user,
        )
        self.payment = create_payment(self.borrowing)
        self.other_payment = create_payment(
            self.other_borrowing, session_id="cs_test_456"
        )

    def test_list_payments_unauthorized(self):
        res = self.client.get(PAYMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_payments_user_sees_only_own(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(PAYMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.payment.id)

    def test_list_payments_user_not_sees_others(self):
        self.client.force_authenticate(self.other_user)
        res = self.client.get(PAYMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.other_payment.id)

    def test_list_payments_admin_sees_all(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(PAYMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_payment_detail_user(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(detail_url(self.payment.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("session_url", res.data)
        self.assertIn("session_id", res.data)

    def test_retrieve_other_user_payment(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(detail_url(self.other_payment.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_payment_admin(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(detail_url(self.other_payment.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_payment_status_pending_by_default(self):
        self.assertEqual(self.payment.status, Payment.StausChoices.PENDING)

    def test_payment_has_correct_borrowing(self):
        self.assertEqual(self.payment.borrowing, self.borrowing)
