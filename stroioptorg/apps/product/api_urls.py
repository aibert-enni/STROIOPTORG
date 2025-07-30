from django.urls import path

from apps.product.views import CartAPIView, \
    ProductByCategoryListAPIView, CategoryTreeAPIView, ShopAddressesAPIView
from apps.product.views.cart import CartProductAPIView
from apps.product.views.product import ProductSearchListAPIView

app_name = 'api-product'

urlpatterns = [
    # cart api
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('cart/product/<int:pk>', CartProductAPIView.as_view(), name='cart-product'),

    # catalog api
    path('catalog/tree/', CategoryTreeAPIView.as_view(), name='category-tree'),
    path('catalog/<slug:category_slug>/', ProductByCategoryListAPIView.as_view(), name='catalog-list'),

    # product api
    path('search/', ProductSearchListAPIView.as_view(), name='search'),

    # shop address api
    path('shop-address/', ShopAddressesAPIView.as_view(), name='shop-addresses')
]
