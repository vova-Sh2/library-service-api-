import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")
        read_only_fields = ("expected_return_date","book", "user", "actual_return_date")


class BorrowingsDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")

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
    def create(self,validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        return super().create(validated_data)
