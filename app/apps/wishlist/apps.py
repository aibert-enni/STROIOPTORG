from django.apps import AppConfig
from django.contrib.auth import user_logged_in


class WishlistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.wishlist'

    def ready(self):
        from . import signals
        user_logged_in.connect(signals.merge_wishlist_on_login)