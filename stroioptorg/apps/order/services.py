from typing import Tuple, Union

from django.conf import settings
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework import status as http_status

import stripe
from rest_framework.request import Request
from stripe import Refund

from apps.order.models import Order, PaymentStatus, PaymentMethod, OrderItem, OrderStatus
from apps.product.models import Cart, CartProduct, Product
from apps.product.services import CartService
from product.models import ShopAddress

stripe.api_key = settings.STRIPE_API_KEY


class OrderService:

    def __init__(self, request):
        self.request = request

    @staticmethod
    def create_order(user=None, *, delivery_method, delivery_cost = 0, address, shop_address, payment_method, comments=None, firstname=None, lastname=None,
                     company=None, mail=None, phone_number=None) -> Tuple[Order, str | None]:

        cart = get_object_or_404(Cart, user=user)

        cart_products = cart.products.all()

        if cart_products.count() <= 0:
            raise ValidationError("Корзина пустая")

        total_price = CartProduct.objects.total_price(cart) + delivery_cost

        if total_price < 1:
            raise ValidationError('Общая сумма в корзине меньше 1')

        errors = []

        for cart_product in cart_products:
            if cart_product.product.stock_quantity < cart_product.quantity:
                errors.append({
                    'message': f'Запрашиваемое количество товара {cart_product.product.name} превышает доступное на складе.',
                    'available_quantity': cart_product.product.stock_quantity,
                })
            else:
                cart_product.product.stock_quantity -= cart_product.quantity
                cart_product.product.save()

        if len(errors) > 0:
            raise ValidationError(errors, code=http_status.HTTP_400_BAD_REQUEST)

        if user:
            firstname = firstname or user.firstname
            lastname = lastname or user.lastname
            mail = mail or user.email
            phone_number = phone_number or user.phone_number

        status = OrderStatus.PENDING_PAYMENT if payment_method == PaymentMethod.CARD else OrderStatus.PROCESSING

        order = Order(user=user, status=status, address=address, total_price=total_price, payment_method=payment_method, payment_status=PaymentStatus.PENDING,
                      delivery_method=delivery_method, delivery_cost=delivery_cost, comments=comments, firstname=firstname,
                      lastname=lastname, company=company, phone_number=phone_number, mail=mail)

        if shop_address:
            shop_address = get_object_or_404(ShopAddress, pk=shop_address)
            order.shop_address = shop_address

        checkout_url = None

        if payment_method == PaymentMethod.CARD:
            order.save()
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {
                            'name': f'Заказ #{order.id}'
                        },
                        'unit_amount': total_price * 100
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'http://localhost:8000/order/success/{order.id}/',
                cancel_url="http://localhost:8000/cancel/",
                metadata={'order_id': order.id},
            )

            order.stripe_payment_id = checkout_session.id

            checkout_url = checkout_session.url

        order.save()

        order_items = []


        for cart_product in cart_products:
            product = cart_product.product
            order_item = OrderItem(order=order, product=product, product_name=product.name, price=product.price, quantity=cart_product.quantity)
            order_items.append(order_item)

        OrderItem.objects.bulk_create(order_items)

        cart.products.all().delete()

        return order, checkout_url

    def retry_payment(self, order_id: int) -> Union[int, None]:
        order = self.get_order(self.request, order_id)

        if order.payment_status == PaymentStatus.SUCCESS:
            raise ValidationError('Заказ уже оплачен')

        if order.payment_method == PaymentMethod.CARD:
            session = stripe.checkout.Session.retrieve(order.stripe_payment_id)
            if session.payment_status == 'paid':
                order.status = OrderStatus.PROCESSING
                order.payment_status = PaymentStatus.SUCCESS
                order.save()
                raise ValidationError('Заказ уже оплачен')
            if session.payment_status == 'expired':
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'rub',
                            'product_data': {
                                'name': f'Заказ #{order.id}'
                            },
                            'unit_amount': order.total_price * 100
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url='http://127.0.0.1:8000/order/success/',
                    cancel_url="http://127.0.0.1:8000/cancel/",
                    metadata={'order_id': order.id},
                )
                order.stripe_payment_id = checkout_session.id

                checkout_url = checkout_session.url
            else:
                checkout_url = session.url
        else:
            raise ValidationError(f'Оплата не через карту, а {order.payment_method}')

        return checkout_url


    def calculate_delivery_cost(self, address) -> int:
        cart = CartService(self.request).get_cart()

        total_price = cart.total_amount

        if total_price < 1:
            raise ValidationError('Общая сумма корзины меньше 1')

        return int(total_price * 0.1)

    def decline_order(self, order_id) -> Order:
        order = get_object_or_404(Order, pk=order_id, user=self.request.user)

        if order.status == OrderStatus.COMPLETED:
            raise ValidationError(f'Заказ №{order.id} уже выполнен')

        if order.status == OrderStatus.CANCELLED:
            raise ValidationError(f'Заказ №{order.id} уже отменен')

        refund = None

        if order.payment_method == PaymentMethod.CARD and order.payment_status == PaymentStatus.SUCCESS:
            refund = self.stripe_refund(order.stripe_payment_id)
            order.payment_status = PaymentStatus.REFUNDED
        else:
            order.payment_status = PaymentStatus.FAILED

        order.status = OrderStatus.CANCELLED
        order.save()

        products_to_update = []

        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            products_to_update.append(item.product)

        Product.objects.bulk_update(products_to_update, ['stock_quantity'])

        if refund is ValidationError:
            raise refund

        return order

    def confirm_order(self, order_id) -> Order:
        order = get_object_or_404(Order, pk=order_id)
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.PENDING_PAYMENT]:
            raise ValidationError(f'Заказ #{order.id} {order.status}')
        order.status = OrderStatus.COMPLETED
        order.payment_status = PaymentStatus.SUCCESS
        order.save()
        return order

    @staticmethod
    def get_order(request: Request, order_id: int) -> Order:
        order = Order.objects.select_related('shop_address').prefetch_related('items').get(pk=order_id)
        return order

    @staticmethod
    def get_orders_by_user(request: Request) -> QuerySet[Order]:
        orders = Order.objects.filter(user=request.user)
        return orders

    @staticmethod
    def stripe_refund(stripe_payment_id) -> Union[Refund, ValidationError]:
        checkout_session = stripe.checkout.Session.retrieve(stripe_payment_id)
        payment_intent_id = checkout_session.payment_intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        charge_id = payment_intent.latest_charge

        charge = stripe.Charge.retrieve(charge_id)

        if not charge:
            return ValidationError(f'charge not found: {charge}')

        if charge.refunded:
            return ValidationError(f'Возврат уже сделан')

        return stripe.Refund.create(charge=charge_id)

    def success_order(self, order_id) -> Order:
        order = self.get_order(self.request, order_id)

        if order.user != self.request.user:
            raise ValidationError("Заказ не принадлежит пользователю")

        if order.payment_status != PaymentStatus.SUCCESS:
            order.payment_status = PaymentStatus.SUCCESS
            order.status = OrderStatus.IN_TRANSIT
            order.save()

        return order
