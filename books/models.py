from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    class ChoicesCover(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=5, choices=ChoicesCover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.title
