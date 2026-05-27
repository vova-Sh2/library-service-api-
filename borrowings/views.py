from django.db import transaction
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingsDetailSerializer, BorrowingsCreateSerializer, BorrowingsSerializer

from notifications import bot_message


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=self.request.user)

        bot_message.send_message(f"📚 Borrowed\n"
                                 f"👤 User: {post.user.email}\n"
                                 f"🪪 First Name: {post.user.first_name}\n"
                                 f"🪪 Last Name: {post.user.last_name}\n"
                                 f"📖 Book: {post.book.title}\n"
                                 f"📦 Inventory: {post.book.inventory}\n"
                                 f"📆 Borrow date: {post.borrow_date}\n"
                                 f"📆 Expected return date: {post.expected_return_date}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()
        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        is_active = self.request.query_params.get("is_active")
        if is_active == "True":
            queryset = queryset.filter(actual_return_date__isnull=True)
        elif is_active == "False":
            queryset = queryset.filter(actual_return_date__isnull=False)
        if not user.is_staff:
            queryset = queryset.filter(user=user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingsDetailSerializer
        if self.action == "create":
            return BorrowingsCreateSerializer
        return BorrowingsSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response({"detail": "This field is required."},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        with transaction.atomic():
            borrowing.actual_return_date = now().date()
            borrowing.save(update_fields=["actual_return_date"])

            book = borrowing.book
            book.inventory += 1
            book.save(update_fields=["inventory"])

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
