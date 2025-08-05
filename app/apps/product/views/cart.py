from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.serializers import CartProductAddSerializer, \
    CartProductUpdateSerializer, CartDataSerializer, CartSuccessResponseSerializer, \
    CartProductAddSuccessResponseSerializer
from apps.product.services import CartProductService, CartService
from utils.serializers import ErrorResponseSerializer, SuccessResponseSerializer


class CartTemplateView(TemplateView):
    template_name = 'product/cart.html'


class CartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='get_cart',
        tags=['cart'],
        summary='Получить корзину данного пользователя',
        description='Возвращает корзину данного пользователя',
        responses={
            200: CartSuccessResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Ошибка 404',
                summary='Корзина не найден',
                description='Пример ответа, когда корзина не найден',
                value={
                    "error": {
                        "code": "http404",
                        "message": "No Cart matches the given query.",
                        "details": {
                            "detail": "No Cart matches the given query."
                        }
                    }
                },
                response_only=True,
                status_codes=["404"]
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        cart = CartService(request).get_cart()
        cart_serializer = CartDataSerializer(cart, context={'total_amount': cart.total_amount})

        return Response({
            'status': 'success',
            'message': 'Корзина получен',
            'data': cart_serializer.data
        }, status=status.HTTP_200_OK)


class CartProductAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='cart add product',
        tags=['cart product'],
        summary='Добавление продукта в корзину',
        description='Для добавления продукта в корзину',
        request=CartProductAddSerializer,
        responses={
            200: CartProductAddSuccessResponseSerializer,
            400: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Когда не хватит количества продукта в складе',
                summary='Когда не хватит количества продукта в складе',
                description='Когда не хватит количества продукта в складе',
                value={
                    'status': 'error',
                    'error': {
                        'code': 'validation_error',
                        'message': 'Invalid input.',
                        'details': {
                            'error': 'В складе количество продукта не хватает для добавления'
                        }
                    }
                },
                response_only=True,
                status_codes=[404]
            )
        ]
    )
    def post(self, request, pk):
        query_serializer = CartProductAddSerializer(data=request.data)

        query_serializer.is_valid(raise_exception=True)

        product_id = pk
        quantity = query_serializer.validated_data['quantity']

        CartProductService(request).create(product_id, quantity)

        return Response({
            'status': 'success',
            'message': 'Продукт был добавлен в корзину',
            'data': {
                'products_added': True
            }
        }, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id='cart update product',
        tags=['cart product'],
        summary='Обновление количества продукта в корзине',
        description='Для обновления количества продукта в корзине',
        request=CartProductUpdateSerializer,
        responses={
            200: SuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Когда не хватит количества продукта в складе',
                summary='Когда не хватит количества продукта в складе',
                description='Когда не хватит количества продукта в складе',
                value={
                    'status': 'error',
                    'error': {
                        'code': 'validation_error',
                        'message': 'Invalid input.',
                        'details': {
                            'error': 'В складе количество продукта не хватает для добавления'
                        }
                    }
                },
                response_only=True,
                status_codes=[404]
            )
        ]
    )
    def put(self, request, pk):
        query_serializer = CartProductUpdateSerializer(data=request.data)

        query_serializer.is_valid(raise_exception=True)

        cart_product_id = pk
        quantity = query_serializer.validated_data['quantity']

        CartProductService(request).update(cart_product_id, quantity)

        return Response({
            'status': 'success',
            'message': 'Продукт в корзине был обновлен',
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['cart product'],
        operation_id='cart remove product',
        summary='Удаление продукта с корзины',
        description='Для удаления продукта с корзину',
        responses={
            400: ErrorResponseSerializer,
        },
    )
    def delete(self, request, pk):
        cart_product_id = pk

        try:
            CartProductService(request).delete(cart_product_id)
        except NotFound as e:
            raise NotFound('Продукт не был найден в корзине')

        return Response({
            'status': 'success',
            'message': 'Продукт был удачно удален с корзины',
        }, status=status.HTTP_204_NO_CONTENT)


class CartRemoveProductAPIView(APIView):

    def delete(self, request, pk):
        cart_product_id = pk

        CartProductService(request).delete(cart_product_id)

        return Response({
            'status': 'success',
            'message': 'Продукт был удачно удален с корзины',
        }, status=status.HTTP_204_NO_CONTENT)
