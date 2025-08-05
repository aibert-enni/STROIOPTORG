from django.core.validators import MinValueValidator
from rest_framework import serializers

from apps.product.models import CartProduct, Cart, Product, Category, ShopAddress
from utils.serializers import SuccessResponseSerializer, BasePaginationDataSerializer


# Product serializers

class ProductSerializer(serializers.ModelSerializer):
    get_discount_price = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'sku', 'discount', 'description', 'price', 'get_discount_price', 'cover_url', 'wishlist']

    def get_discount_price(self, obj):
        return obj.discount_price

    def get_cover_url(self, obj):
        if obj.cover:
            return obj.cover.image.url
        return None

    def get_wishlist(self, obj):
        if obj.wishlist.all():
            return True
        else:
            return False

class ProductGetSuccessResponseSerializer(SuccessResponseSerializer):
    data = ProductSerializer()

class ProductListSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)


class ProductListQuerySerializer(serializers.Serializer):
    order_types = {'price', '-price', '-created_at'}

    order = serializers.ChoiceField(choices=order_types, default='price')

    price_from = serializers.IntegerField(validators=[MinValueValidator(1)], required=False)
    price_to = serializers.IntegerField(validators=[MinValueValidator(1)], required=False)


# Cart serializers

class CartProductUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=True, min_value=1)

class CartProductAddSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=True, min_value=1)

class CartAddSuccessDataSerializer(serializers.Serializer):
    product_added = serializers.BooleanField(default=True)

class CartProductAddSuccessResponseSerializer(SuccessResponseSerializer):
    data = CartAddSuccessDataSerializer()

class CartProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartProduct
        fields = ['id', 'quantity','product', 'subtotal']

class CartDataSerializer(serializers.ModelSerializer):
    total_amount = serializers.IntegerField()
    products = CartProductSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products', 'total_amount']

class CartSuccessResponseSerializer(SuccessResponseSerializer):
    data = CartDataSerializer()

# Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CategoryWithProductsCountSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products_count']

class CategoriesWithProductsCountAndAllProductsCountSerializer(serializers.Serializer):
    categories = CategoryWithProductsCountSerializer(many=True)
    products_count = serializers.IntegerField()

class CategoryTreeDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.CharField()
    children = serializers.ListField(child=serializers.DictField())

class CategoryTreeSuccessResponseSerializer(SuccessResponseSerializer):
    data = CategoryTreeDataSerializer(many=True)

# Search
class SearchQuerySerializer(serializers.Serializer):
    order_types = {'price', '-price', '-created_at'}

    search = serializers.CharField(required=True)
    price_from = serializers.IntegerField(validators=[MinValueValidator(1)], required=False)
    price_to = serializers.IntegerField(validators=[MinValueValidator(1)], required=False)
    order = serializers.ChoiceField(choices=order_types, default='price')

# Shop address

class ShopAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAddress
        fields = '__all__'

class ShopAddressesByCityListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    shops_addresses = ShopAddressSerializer(many=True)

class ShopAddressesByRegionListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    cities = ShopAddressesByCityListSerializer(many=True)

class ShopAddressesSuccessResponseSerializer(SuccessResponseSerializer):
    data = ShopAddressesByRegionListSerializer(many=True)