import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BooksSerializer
from borrowings.models import Borrowing

from payments.serializations import BorrowingPaymentListSerializer, PaymentURLSerializer


class BorrowingsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = (
            "expected_return_date",
            "book",
            "user",
            "actual_return_date",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    payments = BorrowingPaymentListSerializer(many=True, read_only=True)
    book = BooksSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    payments = PaymentURLSerializer(many=True, read_only=True)
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book", "payments")

    def validate_book(self, book):
        if book.inventory == 0:
            raise ValidationError("Expected inventory to be greater than 0")
        return book

    def validate(self, value):
        """expected_return_date there should be more borrow_date"""
        if value["expected_return_date"] <= datetime.date.today():
            raise ValidationError("Expected return date to be greater than borrow_date")
        return value

    @transaction.atomic
    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        return super().create(validated_data)
