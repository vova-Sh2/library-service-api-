from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import UserCreateViewSet, ManageUserViewSet

app_name = "user"


urlpatterns = [
    path("register/", UserCreateViewSet.as_view(), name="register"),
    path("me/", ManageUserViewSet.as_view(), name="manage"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]