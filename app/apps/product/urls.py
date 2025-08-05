from django.urls import path

from apps.product import views
from apps.product.views import ProductsByCategoryView, ProductDetailView
from apps.product.views.cart import CartTemplateView
from apps.product.views.product import ProductSearchTemplateAPIView

app_name = 'product'

urlpatterns = [
    # catalog
    path('catalog/tree', views.get_categories, name='catalog-tree'),
    path('catalog/<slug:category_slug>/', ProductsByCategoryView.as_view(), name='catalog'),
    path('catalog/product/<slug:slug>/', ProductDetailView.as_view(), name='catalog-product'),

    # cart
    path('cart/', CartTemplateView.as_view(), name='cart'),

    # search
    path('products/search/', ProductSearchTemplateAPIView.as_view(), name='products-search'),
]
