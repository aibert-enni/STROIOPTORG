from django.urls import path

from apps.wishlist.views import WishlistListTemplateView

app_name = 'wishlist'

urlpatterns = [
    path('wishlist/list', WishlistListTemplateView.as_view(), name='wishlist_list'),
]