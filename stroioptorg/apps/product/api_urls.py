from django.urls import path

from apps.product.views import CartAPIView, CartAddProductAPIView, CartUpdateProductAPIView, CartRemoveProductAPIView, \
    ProductByCategoryListAPIView, CategoryTreeAPIView, ShopAddressesAPIView
from apps.product.views.product import ProductSearchListAPIView

app_name = 'api-product'

urlpatterns = [
    # cart api
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('cart/add/', CartAddProductAPIView.as_view(), name='cart-add-product'),
    path('cart/update/', CartUpdateProductAPIView.as_view(), name='cart-update-product'),
    path('cart/remove/<int:pk>', CartRemoveProductAPIView.as_view(), name='cart-remove-product'),

    # catalog api
    path('catalog/tree/', CategoryTreeAPIView.as_view(), name='category-tree'),
    path('catalog/<slug:category_slug>/', ProductByCategoryListAPIView.as_view(), name='catalog-list'),

    # product api
    path('search/', ProductSearchListAPIView.as_view(), name='search'),

    # shop address api
    path('shop-address/', ShopAddressesAPIView.as_view(), name='shop-addresses')
]
