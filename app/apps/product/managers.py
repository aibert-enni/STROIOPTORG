from django.db import models
from django.db.models import Sum, F


class CartProductManager(models.Manager):
    def total_price(self, cart):
        return self.filter(cart=cart).aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0