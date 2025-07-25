from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.pagination import OrderPagination
from apps.order.serializers import CreateOrderSerializer, OrderRefreshPaymentSerializer, \
    OrderCalculateDeliveryCostSerializer, OrderDeclineSerializer, OrderResponseSerializer, OrderSerializer, OrderConfirmSerializer
from apps.order.services import OrderService
from utils.permission import IsManager

class OrderView(TemplateView):
    template_name = "product/order.html"

class OrderSuccessView(TemplateView):
    template_name = "product/order_success.html"

class OrderGetAPIView(APIView):

    def get(self, request, pk):
        order = OrderService.get_order(request, pk)
        serializer = OrderResponseSerializer(order)
        return Response({'order': serializer.data})

class OrderListAPIView(ListAPIView):
    serializer_class = OrderResponseSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrderService.get_orders_by_user(self.request)

class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateOrderSerializer,
        description='Для создания заказа',

    )
    def post(self, request):
        query_serializer = CreateOrderSerializer(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        order, checkout_url = OrderService.create_order(request.user, **query_serializer.validated_data)

        if order.stripe_payment_id:
            return Response({'checkout_url': checkout_url})

        return Response({'message': 'Order successfully created', 'order_id': order.id}, status=status.HTTP_201_CREATED)


class OrderRetryPaymentAPIView(APIView):

    @extend_schema(
        request=OrderRefreshPaymentSerializer,
        description='Для повторной оплаты заказа через карту, если в первый раз не смогли оплатить'
    )
    def patch(self, request):
        order_refresh_payment_serializer = OrderRefreshPaymentSerializer(data=request.data)
        order_refresh_payment_serializer.is_valid(raise_exception=True)
        checkout_url = OrderService(request).retry_payment(order_refresh_payment_serializer.validated_data['order_id'])
        return Response({'checkout_url': checkout_url})

class OrderCalculateDeliveryCostAPIView(APIView):

    @extend_schema(
        request=OrderCalculateDeliveryCostSerializer,
        description='Для подсчета стоимости доставки'
    )
    def post(self, request):
        order_calculate_delivery_cost_serializer = OrderCalculateDeliveryCostSerializer(data=request.data)
        order_calculate_delivery_cost_serializer.is_valid(raise_exception=True)

        delivery_cost = OrderService(request).calculate_delivery_cost(order_calculate_delivery_cost_serializer.validated_data['address'])

        return Response({'delivery_cost': delivery_cost})

class OrderDeclineAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=OrderDeclineSerializer,
        description='Для отмены заказа'
    )
    def patch(self, request):
        order_decline_serializer = OrderDeclineSerializer(data=request.data)
        order_decline_serializer.is_valid(raise_exception=True)

        order = OrderService(request).decline_order(order_decline_serializer.validated_data['order_id'])

        return Response({'message': f'Заказ #{order.id} успешно был отменен'})

class OrderConfirmAPIVIew(APIView):
    permission_classes = (IsManager,)

    @extend_schema(
        request=OrderConfirmSerializer,
        description='Подтверждение заказа, например через менеджера или продавца'
    )
    def patch(self, request):
        order_confirm_serializer = OrderConfirmSerializer(data=request.data)
        order_confirm_serializer.is_valid(raise_exception=True)

        order = OrderService(request).confirm_order(order_confirm_serializer.validated_data['order_id'])

        return Response({'message': f'Заказ #{order.id} успешно был подтвержден'})

class OrderSuccessAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema()
    def patch(self, request, pk):

        order = OrderService(request).success_order(pk)

        return Response({'message': f'Заказ успешно был оплачен', "order": order})