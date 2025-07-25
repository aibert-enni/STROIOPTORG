from django.core.validators import MinValueValidator, EmailValidator
from django.db import models

from apps.main.models import TimeStampedModel
from apps.product.models import Product, ShopAddress
from apps.users.models import User
from utils.validators import firstname_validator, lastname_validator, phone_number_validator

class OrderStatus(models.TextChoices):
    COMPLETED = 'completed', 'Выполнен'
    IN_TRANSIT = 'in_transit', 'В пути'
    PROCESSING = 'processing', 'Обработка'
    CANCELLED = 'cancelled', 'Отменен'
    PENDING_PAYMENT = 'pending_payment', 'Не оплачен'

class PaymentMethod(models.TextChoices):
    CARD = 'card', 'Оплата картой на сайте'
    IN_STORE = 'in_store', 'Оплата в магазине'

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидание'
    SUCCESS = 'success', 'Оплачено'
    FAILED = 'failed', 'Ошибка'
    REFUNDED = 'refunded', 'Возврат'
    CANCELED = 'canceled', 'Отменено'

class DeliveryMethod(models.TextChoices):
    PICKUP = 'pickup', 'Самовывоз'
    COURIER = 'courier', 'Курьерская доставка'

class Order(TimeStampedModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True)

    status = models.CharField(choices=OrderStatus, default=OrderStatus.PROCESSING, max_length=20)

    shop_address = models.ForeignKey(ShopAddress, on_delete=models.PROTECT, related_name='orders', null=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    total_price = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    payment_method = models.CharField(choices=PaymentMethod, default=PaymentMethod.CARD, max_length=20)
    payment_status = models.CharField(choices=PaymentStatus, default=PaymentStatus.PENDING, max_length=20)

    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)

    delivery_method = models.CharField(choices=DeliveryMethod, default=DeliveryMethod.COURIER, max_length=20)
    delivery_cost = models.PositiveIntegerField(default=0)

    comments = models.TextField(blank=True, null=True)

    # if user is not authorized
    firstname = models.CharField(max_length=120, validators=[firstname_validator])
    lastname = models.CharField(max_length=120, validators=[lastname_validator])
    company = models.CharField(max_length=120, blank=True, null=True)
    mail = models.CharField(max_length=120, validators=[EmailValidator])
    phone_number = models.CharField(max_length=120, validators=[phone_number_validator])


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    product_name = models.CharField(max_length=255)
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def subtotal(self):
        return self.price * self.quantity

