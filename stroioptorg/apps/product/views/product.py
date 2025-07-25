from django.views.generic import DetailView, TemplateView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView

from apps.product.models import Product, ProductAttribute
from apps.product.pagination import ProductListPagination
from apps.product.serializers import ProductSerializer, CategorySerializer, SearchQuerySerializer
from apps.product.services import ProductService


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product/product.html'

    def get_object(self, queryset=None):
        # Применяем select_related что бы не отправлялся два запроса в бд
        product = Product.objects.prefetch_related('images').get(slug=self.kwargs['slug'])
        self.product = product
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attributes = ProductAttribute.objects.filter(product=self.object).select_related(
            'attribute_value__attribute').order_by('attribute_value__attribute__priority')
        context['attributes'] = attributes
        if attributes:
            type_attribute = attributes.first().attribute_value
            similar_products = Product.objects.exclude(pk=self.product.pk).filter(
                product_attributes__attribute_value=type_attribute)
            context['similar_products'] = similar_products
        return context

@extend_schema(
    parameters=[
        SearchQuerySerializer
    ]
)
class ProductSearchListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductListPagination

    def get_queryset(self):
        query_serializer = SearchQuerySerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)

        return ProductService.search(search_input=query_serializer.data['search'],**query_serializer.data)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        categories = ProductService.get_categories_from_products(self.get_queryset())
        response.data['categories'] = CategorySerializer(categories, many=True).data
        return response

class ProductSearchTemplateAPIView(TemplateView):
    template_name = 'product/search_products.html'