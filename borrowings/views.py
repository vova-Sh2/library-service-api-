from django.db import transaction
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingsListSerializer,
)

from notifications import bot_message
from payments.stripe_session import create_stripe_session


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingsListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)

        create_stripe_session(borrowing)

        bot_message.send_message(
            f"📚 Borrowed\n"
            f"👤 User: {borrowing.user.email}\n"
            f"🪪 First Name: {borrowing.user.first_name}\n"
            f"🪪 Last Name: {borrowing.user.last_name}\n"
            f"📖 Book: {borrowing.book.title}\n"
            f"📦 Inventory: {borrowing.book.inventory}\n"
            f"📆 Borrow date: {borrowing.borrow_date}\n"
            f"📆 Expected return date: {borrowing.expected_return_date}"
        )

    @extend_schema(
        parameters=[
            OpenApiParameter("is_active", bool, description="Filter active borrowings"),
            OpenApiParameter("user_id", int, description="Filter by user (admin only)"),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of borrowed books"""
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()
        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        is_active = self.request.query_params.get("is_active")
        print(type(is_active))
        print(queryset.filter(actual_return_date__isnull=True))
        if is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)
        elif is_active.lower() == "false":
            queryset = queryset.filter(actual_return_date__isnull=False)
        if not user.is_staff:
            queryset = queryset.filter(user=user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingsListSerializer

    @extend_schema(
        description="Return a borrowed book. Sets actual return date and increases book inventory by 1.",
        request=None,
        responses={
            200: BorrowingDetailSerializer,
            400: {"description": "Borrowing already returned"},
        },
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "Borrowing already returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            borrowing.actual_return_date = now().date()
            borrowing.save(update_fields=["actual_return_date"])

            book = borrowing.book
            book.inventory += 1
            book.save(update_fields=["inventory"])

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
