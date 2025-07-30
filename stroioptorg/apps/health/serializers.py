from rest_framework import serializers

from utils.serializers import BaseResponseSerializer


class HealthCheckDataSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.FloatField()
    response_time = serializers.FloatField()
    services = serializers.DictField()

class HealthCheckResponseSerializer(BaseResponseSerializer):
    data = HealthCheckDataSerializer()