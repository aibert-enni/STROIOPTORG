from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from apps.wishlist.models import WishlistProduct


@receiver(user_logged_in)
def merge_wishlist_on_login(sender, request, user, **kwargs):
    wishlist = request.session.get('wishlist', [])
    if len(wishlist) > 0:
        wishlist_products = []
        for product_id in wishlist:
            wishlist_product = WishlistProduct(user=user, product_id=product_id)
            wishlist_products.append(wishlist_product)
        WishlistProduct.objects.bulk_create(wishlist_products, ignore_conflicts=True)