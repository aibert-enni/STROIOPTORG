from itertools import product
from typing import Literal, Union

from django.db.models import QuerySet, F
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

from apps.product.models import Product, CartProduct, Cart
from apps.wishlist.models import WishlistProduct


class WishlistService:
    def __init__(self, request: Request):
        self.request = request

    def get_products_by_user(self) -> QuerySet[Product]:
        return Product.objects.filter(wishlist__user=self.request.user).order_by('-created_at')

    def add_product(self, product_id: int):
        product = get_object_or_404(Product, pk=product_id)

        if self.request.user.is_authenticated:
            WishlistProduct.objects.get_or_create(user=self.request.user, product=product)
        else:
            wishlist = self.request.session.get('wishlist', [])

            if product.id not in wishlist:
                wishlist.append(product.id)
                self.request.session['wishlist'] = wishlist

    def remove_product(self, product_id: int):
        if self.request.user.is_authenticated:
            get_object_or_404(WishlistProduct, product=product_id, user=self.request.user).delete()
        else:
            wishlist = self.request.session.get('wishlist', [])
            if product_id in wishlist:
                wishlist.remove(product_id)
                self.request.session['wishlist'] = wishlist

    def toggle(self, product_id: int) -> Literal['added', 'removed']:
        status: Literal['added', 'removed']

        product = get_object_or_404(Product, pk=product_id)

        if self.request.user.is_authenticated:
            wishlist_product, created = WishlistProduct.objects.get_or_create(user=self.request.user, product=product)
            if not created:
                wishlist_product.delete()
                status = 'removed'
            else:
                status = 'added'
        else:
            wishlist = self.request.session.get('wishlist', [])
            if product_id in wishlist:
                wishlist.remove(product_id)
                status = 'removed'
            else:
                wishlist.append(product_id)
                status = 'added'
            self.request.session['wishlist'] = wishlist

        return status

    def check_product(self, product_id: int) -> bool:
        if self.request.user.is_authenticated:
            return WishlistProduct.objects.filter(user=self.request.user, product=product_id).exists()
        else:
            wishlist = self.request.session.get('wishlist', [])
            if product_id in wishlist:
                return True

    @atomic
    def move_products_to_cart(self) -> [CartProduct]:
        wishlists = WishlistProduct.objects.filter(
            user=self.request.user,
            product__stock_quantity__gt=0
        )

        if not wishlists.exists():
            raise ValidationError('У пользователя нет продуктов которых можно добавить в корзину')

        cart, created = Cart.objects.get_or_create(user=self.request.user)

        # Get products not already in cart
        existing_cart_products = set(
            CartProduct.objects.filter(cart=cart).values_list('product_id', flat=True)
        )

        products_to_add = wishlists.exclude(
            product_id__in=existing_cart_products
        ).select_related('product')

        cart_products_to_create = [
            CartProduct(product=wishlist.product, cart=cart, quantity=1)
            for wishlist in products_to_add
        ]

        if cart_products_to_create:
            created_products = CartProduct.objects.bulk_create(cart_products_to_create)

            # Update stock atomically
            product_ids = [cp.product.id for cp in cart_products_to_create]
            Product.objects.filter(
                id__in=product_ids,
                stock_quantity__gte=1
            ).update(stock_quantity=F('stock_quantity') - 1)

            wishlists.delete()
            return created_products

        return []

    def clear_wishlist(self):
        products = WishlistProduct.objects.filter(user=self.request.user)
        deleted_count, _ = products.delete()

        return deleted_count