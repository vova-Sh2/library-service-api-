from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    class StausChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        max_length=10, choices=StausChoices.choices, default=StausChoices.PENDING
    )
    type = models.CharField(
        max_length=10, choices=TypeChoices.choices, default=TypeChoices.PAYMENT
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(null=True, blank=True)
    session_id = models.CharField(max_length=155, null=True, blank=True)
    money_to_pay = models.DecimalField(max_digits=8, decimal_places=2)
