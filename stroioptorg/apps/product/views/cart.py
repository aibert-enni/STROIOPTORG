from django.db.models import Prefetch
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import CartProduct, Cart
from apps.product.serializers import CartSerializer, CartProductSerializer, UpdateCartProductSerializer, \
    AddToCartSerializer
from apps.product.services import CartProductService, CartService


class CartTemplateView(TemplateView):
    template_name = 'product/cart.html'

class CartAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartSerializer

    def get(self, request, *args, **kwargs):
        cart = CartService(request).get_cart()
        cart_serializer = CartSerializer(cart, context={'total_amount': cart.total_amount})

        return Response(cart_serializer.data, status=status.HTTP_200_OK)


class CartAddProductAPIView(APIView):
    @extend_schema(
        request=AddToCartSerializer,
        description='Для добавления продукта в корзину'
    )
    def post(self, request):
        query_serializer = AddToCartSerializer(data=request.data)

        query_serializer.is_valid(raise_exception=True)

        product_id = query_serializer.validated_data['product_id']
        quantity = query_serializer.validated_data['quantity']

        # Serialize cart for response
        cart = CartProductService(request).create(product_id, quantity)

        cart = Cart.objects.prefetch_related(
            Prefetch('products', queryset=CartProduct.objects.select_related('product__cover'))
        ).get(pk=cart.pk)

        cart_serializer = CartSerializer(cart, context={'total_amount': cart.total_amount})

        return Response({
            'status': 'success',
            'message': 'Продукт был добавлен в корзину удачно',
            'cart': cart_serializer.data,
        }, status=status.HTTP_200_OK)


class CartUpdateProductAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=UpdateCartProductSerializer,
        description='Для обновления количества продуктов в корзине'
    )
    def put(self, request):
        query_serializer = UpdateCartProductSerializer(data=request.data)

        query_serializer.is_valid(raise_exception=True)

        cart_product_id = query_serializer.validated_data['cart_product_id']
        quantity = query_serializer.validated_data['quantity']

        cart_product = CartProductService(request).update(cart_product_id, quantity)

        cart_product_serializer = CartProductSerializer(cart_product)

        return Response({
            'status': 'success',
            'message': 'Продукт в корзине удачно был обновлен',
            'cart': cart_product_serializer.data
        }, status=status.HTTP_200_OK)


class CartRemoveProductAPIView(APIView):

    def delete(self, request, pk):
        cart_product_id = pk

        CartProductService(request).delete(cart_product_id)

        return Response({
            'status': 'success',
            'message': 'Продукт был удачно удален с корзины',
        }, status=status.HTTP_204_NO_CONTENT)
