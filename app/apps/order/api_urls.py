from django.urls import path

from apps.order.views import OrderCreateAPIView, OrderRetryPaymentAPIView, OrderCalculateDeliveryCostAPIView, \
    OrderDeclineAPIView, OrderGetAPIView, OrderListAPIView, OrderConfirmAPIVIew, OrderSuccessAPIView
from apps.order.webhooks import stripe_webhook

app_name = 'order'

urlpatterns = [
    # get
    path('order/<int:pk>/', OrderGetAPIView.as_view(), name='order'),
    path('order/list/me/', OrderListAPIView.as_view(), name='orders-me'),

    # post
    path('order/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('order/retry-payment/', OrderRetryPaymentAPIView.as_view(), name='order-refresh'),
    path('order/calculate-delivery/', OrderCalculateDeliveryCostAPIView.as_view(), name='order-calculate-delivery'),

    # patch
    path('order/decline/', OrderDeclineAPIView.as_view(), name='order-decline'),
    path('order/confirm/', OrderConfirmAPIVIew.as_view(), name='order-confirm'),
    path('order/success/<int:pk>/', OrderSuccessAPIView.as_view(), name='order-success'),

    # webhook
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]