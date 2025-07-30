from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.serializers import ProductSerializer, CategoryWithProductsCountSerializer, \
    CategoriesWithProductsCountAndAllProductsCountSerializer
from apps.product.services import ProductService
from apps.wishlist.serializers import WishlistAddSerializer, WishlistToggleSerializer, \
    WishlistToggleSuccessResponseSerializer, WishlistCheckProductSuccessResponseSerializer
from apps.wishlist.services import WishlistService
from utils.pagination import BasePagination
from utils.serializers import SuccessResponseSerializer


class WishlistListTemplateView(TemplateView):
    template_name = 'product/wishlists.html'


@extend_schema(
    operation_id='wishlist list me',
    tags=['wishlist'],
    summary='Список избранных данного пользователя',
    description='Список избранных данного пользователя',
    responses={
        200: ProductSerializer
    }
)
class WishlistListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    pagination_class = BasePagination

    def get_queryset(self):
        return WishlistService(self.request).get_products_by_user()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        categories = ProductService.get_categories_from_products(self.get_queryset())
        categories_serializer = CategoryWithProductsCountSerializer(categories, many=True)
        serializer = CategoriesWithProductsCountAndAllProductsCountSerializer(
            {"categories": categories_serializer.data, "products_count": self.get_queryset().count()})
        response.data['categories'] = serializer.data
        return response


class WishlistAddAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='add product to user wishlist',
        tags=['wishlist'],
        summary='Добавить товар в список избранного',
        description='Добавляем товар в избранное, если пользователь авторизован в базу данные, если нет, то сохраняем в сессии',
        request=WishlistAddSerializer,
        responses={
            201: SuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа',
                value={
                    'status': 'success',
                    'message': 'Товар добавлен в список желаемого'
                },
                response_only=True
            )
        ]
    )
    def post(self, request, pk):
        WishlistService(request).add_product(pk)

        return Response({
            'status': 'success',
            'message': 'Товар добавлен в список желаемого',
        }, status=status.HTTP_201_CREATED)


class WishlistRemoveAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='remove product from user wishlist',
        tags=['wishlist'],
        summary='Удаляем товар из списка избранного данного пользователя',
        description='Удаляем товар из списка желаемого',
    )
    def delete(self, request, pk):
        WishlistService(request).remove_product(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)


class WishlistToggleAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='toggle product from user wishlist',
        tags=['wishlist'],
        summary='Добавить или удалить товар с избранного(работает как переключатель)',
        description='Добавить или удалить товар с избранного(работает как переключатель)',
        request=WishlistToggleSerializer,
        responses={
            200: WishlistToggleSuccessResponseSerializer
        },
    )
    def post(self, request):
        toggle_serializer = WishlistToggleSerializer(data=request.data)
        toggle_serializer.is_valid(raise_exception=True)

        product_id = toggle_serializer.validated_data['product_id']

        wishlist_status = WishlistService(request).toggle(product_id)

        return Response({
            'status': 'success',
            'message': 'Товар добавлен в избранные' if wishlist_status == 'added' else 'Товар удален с избранного',
            'data': {
                'status': wishlist_status,
                'product_id': product_id
            }
        }, status=status.HTTP_200_OK)


class WishlistClearAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='wishlist clear user wishlist',
        tags=['wishlist'],
        summary='Очистка списка избранного данного пользователя',
        description='Очистка списка избранного',
        responses={
            200: SuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа',
                value={
                    'status': 'success',
                    'message': 'Избранное очищено'
                }
            ),
            OpenApiExample(
                'Пример ответа если список пустой',
                summary='Пример ответа если список пустой',
                description='Пример ответа если список пустой',
                value={
                    'status': 'success',
                    'message': 'Избранное уже было пустым'
                }
            )
        ]
    )
    def post(self, request):
        deleted_count = WishlistService(request).clear_wishlist()

        message = 'Избранное очищено' if deleted_count > 0 else 'Избранное уже было пустым'
        return Response({
            'status': 'success',
            'message': message,
        }, status=status.HTTP_200_OK)


class WishlistCheckProductAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='check product in wishlist',
        tags=['wishlist'],
        summary='Проверяем есть ли продукт в списке желаемого данного пользователя',
        description='Проверяем есть ли продукт в списке желаемого данного пользователя',
        responses=WishlistCheckProductSuccessResponseSerializer,
    )
    def get(self, request, pk):
        product_status = WishlistService(request).check_product(pk)
        return Response({
            'status': 'success',
            'message': 'Продукт в списке' if product_status else 'Продукт не в списке',
            'data': {
                'is_in_wishlist': product_status,
                'product_id': pk
            },
        }, status=status.HTTP_200_OK)


class WishlistMoveToCartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='move wishlist products to cart',
        tags=['wishlist'],
        summary='Перемещаем продукты с избранного в корзину данного пользователя',
        description='Перемещаем продукты с избранного в корзину данного пользователя',
        responses={
            200: SuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа',
                value={
                    'status': 'success',
                    'message': 'Продукты успешно добавлены в корзину',
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        WishlistService(request).move_products_to_cart()
        return Response({
            'status': 'success',
            'message': 'Продукты успешно добавлены в корзину'
        }, status=status.HTTP_200_OK)
