import time

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as status_codes

from apps.health.serializers import HealthCheckResponseSerializer
from apps.health.services import ServiceHealthChecker
from utils.serializers import SuccessResponseSerializer


# Create your views here.

class HealthCheckAPIView(APIView):

    @extend_schema(
        operation_id='health_check',
        summary='Проверка состояния внутренних сервисов(redis, database, elasticsearch)',
        description='Позволяет посмотреть состояние внутренних сервисов(redis, database, elasticsearch)',
        tags=['health check'],
        responses={
            200: HealthCheckResponseSerializer,
            503: HealthCheckResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа для проверки состояния внутренних сервисов',
                value={
                    'status': 'success',
                    'message': '',
                    'data': {
                        "status": "healthy",
                        "timestamp": 1753803025.9886327,
                        "response_time": 462.58,
                        "services": {
                            "database": {
                                "status": "healthy",
                                "migration_count": 77,
                                "queries_executed": 3,
                                "vendor": "sqlite"
                            },
                            "redis": {
                                "status": "healthy",
                                "version": "7.4.5",
                                "connected_clients": 1,
                                "used_memory_human": "1.08M",
                                "keyspace_hits": 190,
                                "keyspace_misses": 5
                            },
                            "elasticsearch": {
                                "status": "healthy",
                                "cluster_name": "docker-cluster",
                                "cluster_status": "yellow",
                                "number_of_nodes": 1,
                                "active_primary_shards": 2,
                                "active_shards": 2,
                                "relocating_shards": 0,
                                "initializing_shards": 0,
                                "unassigned_shards": 2
                            }
                        }
                    }
                },
                response_only=True
            ),
        ]
    )
    def get(self, request):
        start_time = time.time()

        # Check all services
        db_status = ServiceHealthChecker.check_database_detailed()
        redis_status = ServiceHealthChecker.check_redis_detailed()
        es_status = ServiceHealthChecker.check_elasticsearch_detailed()

        # Determine overall status
        all_healthy = all(
            status['status'] == 'healthy'
            for status in [db_status, redis_status, es_status]
            if status['status'] != 'unavailable'
        )

        response_data = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': time.time(),
            'response_time': round((time.time() - start_time) * 1000, 2),  # ms
            'services': {
                'database': db_status,
                'redis': redis_status,
                'elasticsearch': es_status
            }
        }

        if all_healthy:
            return Response({
                'status': 'success',
                'message': 'Сервисы работают исправно',
                'data': response_data
            }, status=status_codes.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Сервисы неисправны',
                'data': response_data
            }, status=status_codes.HTTP_503_SERVICE_UNAVAILABLE)
