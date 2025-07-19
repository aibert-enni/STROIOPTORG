import logging

from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.product.models import Cart
from apps.product.models import Category
from apps.product.utils import get_nested_categories
from utils.cache import safe_cache_set

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    old_session_key = request.session.get('old_session_key', None)
    if old_session_key:
        session_cart = Cart.objects.filter(session_key=old_session_key).first()
        if session_cart:
            user_cart = Cart.objects.filter(user=user).first()
            if user_cart and user_cart != session_cart:
                session_cart.user = user
                session_cart.save()
                user_cart.delete()
            else:
                session_cart.user = user
                session_cart.save()

@receiver(post_save, sender=Category)
def update_nested_categories_cache(sender, instance, created, **kwargs):
    categories = Category.objects.select_related('parent')
    # Получаем дерево категории каталога
    nested_categories = get_nested_categories(categories)
    safe_cache_set("nested_categories", nested_categories)