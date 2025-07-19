import logging
import traceback

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import exceptions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error

from redis.exceptions import ConnectionError
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

def drf_custom_exception_handler(exc, context):
    view = context.get('view')
    request = context.get('request')

    logger.error(
        f"❌ Exception in view: {view.__class__.__name__ if view else 'Unknown'} "
        f"Method: {request.method} Path: {request.path if request else 'unknown'}"
    )

    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    response = exception_handler(exc, context)

    if isinstance(exc, IntegrityError):
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, ConnectionError):
        logger.error(str(exc))
        return Response({'detail': "Сервис временно недоступен. Попробуйте позже"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if response is None and isinstance(exc, ValidationError):
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    if response is not None:
        if isinstance(response.data, dict):
            response.data['status_code'] = response.status_code
        logger.error(response.data)
        return response
    return response