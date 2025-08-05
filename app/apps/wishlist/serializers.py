from rest_framework import serializers


class WishlistAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

class WishlistToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

class WishlistToggleDataSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['added', 'removed'])
    product_id = serializers.IntegerField()

class WishlistToggleSuccessResponseSerializer(serializers.Serializer):
    data = WishlistToggleDataSerializer()

class WishlistCheckProductDataSerializer(serializers.Serializer):
    is_in_wishlist = serializers.BooleanField()
    product_id = serializers.IntegerField()

class WishlistCheckProductSuccessResponseSerializer(serializers.Serializer):
    data = WishlistCheckProductDataSerializer()