from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from user.serializers import UserSerializer


class UserCreateViewSet(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()


class ManageUserViewSet(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
