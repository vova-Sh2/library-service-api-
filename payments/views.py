from django.conf import settings
from django import views
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from payments.models import Payment
from payments.serializations import PaymentSerializer, CreatePaymentSerializer, PaymentDetailSerializer

import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(views.View):
    def post(self, request):
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Test"
                        },
                        "unit_amount": 2000,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/",
        )
        return

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CreatePaymentSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer
