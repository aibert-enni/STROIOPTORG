from rest_framework import serializers

from apps.review.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ReviewCreateSerializer(serializers.Serializer):
    order_item_id = serializers.IntegerField()
    score = serializers.FloatField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False)

class ReviewUpdateSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    score = serializers.FloatField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False)