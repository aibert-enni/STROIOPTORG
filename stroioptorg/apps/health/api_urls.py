from django.urls import path

from apps.health.views import HealthCheckAPIView

app_name = 'api-health'

urlpatterns = [
    path('health/check/', HealthCheckAPIView.as_view(), name='health_check'),
]