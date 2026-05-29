from django.conf import settings
from django import views
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializations import PaymentSerializer, CreatePaymentSerializer, PaymentDetailSerializer

import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CreatePaymentSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer
