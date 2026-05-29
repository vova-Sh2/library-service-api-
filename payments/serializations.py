from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "borrowing", "money_to_pay")


class BorrowingPaymentListSerializer(PaymentSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "money_to_pay")

class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("type", "borrowing", "money_to_pay")


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "borrowing", "session_url", "session_id", "money_to_pay")

