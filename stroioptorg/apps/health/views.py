import time

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as status_codes

from apps.health.services import ServiceHealthChecker


# Create your views here.

class HealthCheckAPIView(APIView):
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

        status_code = status_codes.HTTP_200_OK if all_healthy else status_codes.HTTP_503_SERVICE_UNAVAILABLE

        return Response(response_data, status=status_code)