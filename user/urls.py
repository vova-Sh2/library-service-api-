from django.urls import path

from user.views import UserCreateViewSet, ManageUserViewSet

app_name = "user"


urlpatterns = [
    path("register/", UserCreateViewSet.as_view(), name="register"),
    path("me/", ManageUserViewSet.as_view(), name="manage"),
]