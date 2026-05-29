from django.urls import path, include
from rest_framework import routers

from payments.views import PaymentViewSet, CreateCheckoutSessionView

app_name = "payments"
router = routers.DefaultRouter()
router.register("", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    # path(
    #     "create-checkout-session/",
    #     CreateCheckoutSessionView.as_view(),
    #     name="create-checkout-session"
    # ),
]