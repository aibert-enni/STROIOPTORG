from rest_framework import serializers


class BaseResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['success', 'error'])
    message = serializers.CharField()

class SuccessResponseSerializer(BaseResponseSerializer):
    status = serializers.CharField(default='success', read_only=True)
    data = serializers.DictField(required=False)

class ErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField()


class ErrorResponseSerializer(BaseResponseSerializer):
    status = serializers.CharField(default='error', read_only=True)
    error = ErrorSerializer()

    message = None

class BasePaginationDataSerializer(serializers.Serializer):
    current_page = serializers.IntegerField()
    max_page = serializers.IntegerField()
    count = serializers.IntegerField()
    next = serializers.URLField()
    previous = serializers.URLField()
    results = serializers.DictField()