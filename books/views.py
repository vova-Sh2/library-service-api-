from rest_framework.viewsets import ModelViewSet

from books.models import Book
from books.permissions import IsAdminOrIfAuthenticatedReadOnly
from books.serializers import BooksSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
