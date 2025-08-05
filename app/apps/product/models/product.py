import uuid

from django.core.validators import MinValueValidator
from django.db import models

from apps.main.models import TimeStampedModel


class ProductImage(models.Model):
    image = models.ImageField(verbose_name='Изображение')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

class Product(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name='Название')
    images = models.ManyToManyField(ProductImage, related_name='products', verbose_name='Изображения')
    cover = models.ForeignKey(ProductImage, on_delete=models.CASCADE, null=True, blank=True, related_name='cover')
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True, editable=False, blank=True)
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Цена')
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    discount = models.IntegerField(verbose_name='Скидка', null=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    @property
    def get_discount_price(self) -> int:
        if self.discount:
            return int(self.price - (self.price * (self.discount * 0.01)))
        return self.price

    def save(self, **kwargs):
        if not self.sku:
            self.sku = uuid.uuid4().hex[:8].upper()
        super().save(**kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'