from django.db import models

from apps.users.models import City


class ShopAddress(models.Model):
    street = models.CharField(max_length=200, verbose_name="Адрес")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город", related_name="shops_addresses")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
    business_hours = models.JSONField(default=dict, verbose_name="Рабочие часы")

    def __str__(self):
        return f"{self.postal_code}, {self.city.name}, {self.street}"

    @property
    def full_address(self):
        return f"{self.postal_code}, {self.city.name}, {self.street}"

    class Meta:
        verbose_name = "Адрес магазина"
        verbose_name_plural = "Адреса магазинов"