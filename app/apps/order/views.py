from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.serializers import CreateOrderSerializer, OrderRefreshPaymentSerializer, \
    OrderCalculateDeliveryCostSerializer, OrderDeclineSerializer, \
    OrderConfirmSerializer, OrderGetSuccessResponseSerializer, OrderDataSerializer, \
    CreateOrderSuccessResponseSerializer, RetryOrderSuccessResponseSerializer, \
    OrderCalculateDeliveryCostSuccessResponseSerializer, OrderSerializer, OrderSuccessSuccessResponseSerializer
from apps.order.services import OrderService
from utils.pagination import BasePagination
from utils.permission import IsManager
from utils.serializers import SuccessResponseSerializer


class OrderView(TemplateView):
    template_name = "product/order.html"


class OrderSuccessView(TemplateView):
    template_name = "product/order_success.html"


class OrderGetAPIView(APIView):

    @extend_schema(
        operation_id='order get',
        tags=['order'],
        summary='Получить заказ по id',
        description='Получить заказ по id',
        responses={
            200: OrderGetSuccessResponseSerializer
        }
    )
    def get(self, request, pk):
        order = OrderService.get_order(request, pk)
        serializer = OrderDataSerializer(order)
        return Response({
            'status': 'success',
            'message': 'Заказ получен',
            'data': serializer.data
        })


@extend_schema(
    operation_id='order get user list',
    tags=['order'],
    summary='Получить заказы данного пользователя',
    description='Получить заказы данного пользователя',
    responses={
        200: OrderDataSerializer
    }
)
class OrderListAPIView(ListAPIView):
    serializer_class = OrderDataSerializer
    pagination_class = BasePagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrderService.get_orders_by_user(self.request)


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='order create',
        tags=['order'],
        summary='Создание заказа',
        description='Для создания заказа',
        request=CreateOrderSerializer,
        responses={
            201: CreateOrderSuccessResponseSerializer
        }
    )
    def post(self, request):
        query_serializer = CreateOrderSerializer(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        order, checkout_url = OrderService.create_order(request.user, **query_serializer.validated_data)

        return Response({
            'status': 'success',
            'message': 'Заказ создан',
            'data': {
                'order_id': order.id,
                'checkout_url': checkout_url if order.stripe_payment_id else ''
            }
        }, status=status.HTTP_201_CREATED)


class OrderRetryPaymentAPIView(APIView):

    @extend_schema(
        operation_id='order retry payment',
        tags=['order'],
        summary='Для повторной оплаты через карту, если в первый раз не смогли оплатить',
        description='Для повторной оплаты заказа через карту, если в первый раз не смогли оплатить',
        request=OrderRefreshPaymentSerializer,
        responses={
            200: RetryOrderSuccessResponseSerializer
        }
    )
    def post(self, request):
        order_refresh_payment_serializer = OrderRefreshPaymentSerializer(data=request.data)
        order_refresh_payment_serializer.is_valid(raise_exception=True)
        checkout_url = OrderService(request).retry_payment(order_refresh_payment_serializer.validated_data['order_id'])
        return Response({
            'status': 'success',
            'message': 'Повторная оплата доступна',
            'data': {
                'checkout_url': checkout_url
            }
        })


class OrderCalculateDeliveryCostAPIView(APIView):

    @extend_schema(
        operation_id='order calculate delivery cost',
        tags=['order'],
        summary='Подсчитать стоимость доставки',
        description='Для подсчета стоимости доставки',
        request=OrderCalculateDeliveryCostSerializer,
        responses={
            200: OrderCalculateDeliveryCostSuccessResponseSerializer
        }
    )
    def post(self, request):
        order_calculate_delivery_cost_serializer = OrderCalculateDeliveryCostSerializer(data=request.data)
        order_calculate_delivery_cost_serializer.is_valid(raise_exception=True)

        delivery_cost = OrderService(request).calculate_delivery_cost(
            order_calculate_delivery_cost_serializer.validated_data['address'])

        return Response({
            'status': 'success',
            'message': 'Подсчет получен',
            'data': {
                'delivery_cost': delivery_cost
            }
        })


class OrderDeclineAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='order decline',
        tags=['order'],
        summary='Отмена заказа',
        description='Для отмены заказа',
        request=OrderDeclineSerializer,
        responses={
            200: SuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary='Пример успешного ответа',
                description='Пример успешного ответа',
                value={
                    'status': 'success',
                    'message': f'Заказ #20 успешно отменен'
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        order_decline_serializer = OrderDeclineSerializer(data=request.data)
        order_decline_serializer.is_valid(raise_exception=True)

        order = OrderService(request).decline_order(order_decline_serializer.validated_data['order_id'])

        return Response({
            'status': 'success',
            'message': f'Заказ #{order.id} успешно отменен'
        })


class OrderConfirmAPIVIew(APIView):
    permission_classes = (IsManager,)

    @extend_schema(
        operation_id='order confirm',
        tags=['order'],
        summary='Подтверждение заказа',
        description='Подтверждение заказа, например через менеджера или продавца',
        request=OrderConfirmSerializer,
        responses={
            200: SuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary='Пример успешного ответа',
                description='Пример успешного ответа',
                value={
                    'status': 'success',
                    'message': f'Заказ #20 успешно подтвержден'
                },
                response_only=True
            )
        ]
    )
    def patch(self, request):
        order_confirm_serializer = OrderConfirmSerializer(data=request.data)
        order_confirm_serializer.is_valid(raise_exception=True)

        order = OrderService(request).confirm_order(order_confirm_serializer.validated_data['order_id'])

        return Response({'message': f'Заказ #{order.id} успешно был подтвержден'})


class OrderSuccessAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='order confirm',
        tags=['order'],
        summary='Проверить оплачен ли заказ',
        description='Проверить оплачен ли заказ через карту',
        responses={
            200: OrderSuccessSuccessResponseSerializer
        },
    )
    def post(self, request, pk):
        order = OrderService(request).success_order(pk)
        data_serializer = OrderSerializer(order)
        return Response({
            'status': 'success',
            'message': f'Заказ #{pk} успешно оплачен',
            'data': data_serializer.data
        })
