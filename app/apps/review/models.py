from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.main.models import TimeStampedModel
from apps.product.models import Product
from apps.users.models import User


class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def save(self, *args, **kwargs):
        self.score = round(self.score, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}: {self.user} - {self.product} ({self.score}★)'