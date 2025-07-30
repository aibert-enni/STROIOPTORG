from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from silk.profiling.profiler import silk_profile

from apps.product.models import Category, Product
from apps.product.serializers import ProductSerializer, ProductListQuerySerializer, \
    CategoryTreeSuccessResponseSerializer
from apps.product.services import ProductByCategoryListService
from apps.product.utils import get_nested_categories, get_filter
from utils.cache import safe_cache_get, safe_cache_set
from utils.pagination import BasePagination


def get_categories(request):
    categories = Category.objects.select_related('parent')
    # Получаем дерево категории каталога
    nested_categories = get_nested_categories(categories)
    return JsonResponse(nested_categories, safe=False)


class ProductsByCategoryView(ListView):
    model = Product
    context_object_name = 'products'
    paginate_by = 9
    template_name = 'product/catalog.html'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')

        category = get_object_or_404(Category, slug=category_slug)

        self.category = category

        products = ProductByCategoryListService(category).get_products(user=self.request.user)

        self.products = products

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data['category'] = self.category

        products = self.products

        filters = {}

        category_filters = self.category.filter_attributes.filter(is_filterable=True).prefetch_related('attribute')

        for category_filter in category_filters:
            filters[category_filter.attribute.filter_name] = {
                'name': category_filter.attribute.name,
                'values': get_filter(category_filter.attribute, products)
            }

        context_data['filters'] = filters

        context_data['total_products'] = self.products.count()

        return context_data


class CategoryTreeAPIView(APIView):

    @extend_schema(
        operation_id='get category tree',
        summary='Получить древо категории',
        description='Получаем иерархию категории',
        responses={
            200: CategoryTreeSuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа',
                value=[
                    {
                        "id": 1,
                        "name": "Инструмент",
                        "url": "instrument",
                        "children": [
                            {
                                "id": 2,
                                "name": "Электроинструмент",
                                "url": "elektroinstrument",
                                "children": [
                                    {
                                        "id": 3,
                                        "name": "Дрели, шуруповерты и гайковерты",
                                        "url": "dreli-shurupoverty-i-gajkoverty",
                                        "children": []
                                    },
                                    {
                                        "id": 4,
                                        "name": "Перфоратор",
                                        "url": "perforator",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                ],
                response_only=True
            )
        ]
    )
    def get(self, request):
        nested_categories = safe_cache_get("nested_categories")

        if not nested_categories:
            categories = Category.objects.select_related('parent')
            # Получаем дерево категории каталога
            nested_categories = get_nested_categories(categories)
            safe_cache_set("nested_categories", nested_categories)

        return Response(nested_categories)


@extend_schema(
    operation_id='get catalog',
    tags=['catalog'],
    summary='Получаем каталог товаров',
    description='Получаем каталог товаров по slug с фильтрами, еще можно делать фильтр с помощью атрибутов товара',
    parameters=[ProductListQuerySerializer],
)
class ProductByCategoryListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = BasePagination

    @silk_profile()
    def get_queryset(self):
        query_serializer = ProductListQuerySerializer(data=self.request.query_params)

        query_serializer.is_valid(raise_exception=True)

        category_slug = self.kwargs.get('category_slug')
        order = query_serializer.data.get('order')
        price_from = query_serializer.data.get('price_from')
        price_to = query_serializer.data.get('price_to')

        category = get_object_or_404(Category, slug=category_slug)

        products = ProductByCategoryListService(category).get_products(price_from, price_to, order,
                                                                       self.request.query_params,
                                                                       user=self.request.user)

        return products
