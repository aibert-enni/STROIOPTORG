from django.urls import path

from apps.order.views import OrderView, OrderSuccessView

app_name = 'order'

urlpatterns = [
    path('order', OrderView.as_view(), name='order'),
    path('order/success/<int:pk>/', OrderSuccessView.as_view(), name='order-success'),
]