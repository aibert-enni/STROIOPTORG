from django.apps import AppConfig
from django.contrib.auth import user_logged_in


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'
    label = 'product'

    def ready(self):
        from . import signals
        user_logged_in.connect(signals.merge_cart_on_login)
