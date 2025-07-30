from django.urls import path

from apps.wishlist.views import WishlistAddAPIView, WishlistRemoveAPIView, WishlistToggleAPIView, WishlistListAPIView, \
    WishlistClearAPIView, WishlistCheckProductAPIView, WishlistMoveToCartAPIView

app_name = 'api-wishlist'

urlpatterns = [
    path('wishlist/add/<int:pk>/', WishlistAddAPIView.as_view(), name='wishlist-add'),
    path('wishlist/remove/<int:pk>/', WishlistRemoveAPIView.as_view(), name='wishlist-remove'),
    path('wishlist/toggle/', WishlistToggleAPIView.as_view(), name='wishlist-toggle'),

    path('wishlist/list/me/', WishlistListAPIView.as_view(), name='wishlist-list'),
    path('wishlist/clear/me/', WishlistClearAPIView.as_view(), name='wishlist-clear'),
    path('wishlist/check-product/<int:pk>/', WishlistCheckProductAPIView.as_view(), name='wishlist-check-product'),
    path('wishlist/move_to_cart/me/', WishlistMoveToCartAPIView.as_view(), name='wishlist-move_to_cart'),
]