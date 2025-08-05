import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, OperationalError as DBConnectionError
from rest_framework import exceptions, status, serializers
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error

from redis.exceptions import ConnectionError
from rest_framework.views import exception_handler
from elasticsearch import ConnectionError as ESConnectionError

from utils.serializers import ErrorResponseSerializer

logger = logging.getLogger(__name__)


def drf_custom_exception_handler(exc, context):
    view = context.get('view')
    request = context.get('request')

    logger.error(
        f"❌ Exception in view: {view.__class__.__name__ if view else 'Unknown'}\n"
        f"Method: {request.method} Path: {request.path if request else 'unknown'}\n"
        f"Message: {exc}"
    )

    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, IntegrityError):
            serializer = ErrorResponseSerializer({
                'error': {
                    'code': 'INTEGRITY_ERROR',
                    'message': "Integrity Error",
                    'details': {
                        'error': ''
                    }
                }
            })
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, NotFound):
            serializer = ErrorResponseSerializer({
                "error": {
                    "code": "NOT_FOUND_ERROR",
                    "message": "Resource not found",
                    "details": str(exc)
                }
            })
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, (ConnectionError, DBConnectionError, ESConnectionError)):
            serializer = ErrorResponseSerializer({
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Service unavailable right now. Try again later",
                    'details': {'error': 'Service unavailable'}
                }
            })
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            serializer = ErrorResponseSerializer({
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal Server Error",
                    "details": {'error': 'Internal Server Error'}
                }
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(serializer.data, status=status_code)

    detail = getattr(exc, 'detail', None)

    if isinstance(detail, (list, dict)):
        message = 'Invalid input.'
    else:
        message = detail or str(exc)

    serializer = ErrorResponseSerializer({
        'error': {
            'code': exc.__class__.__name__.lower(),
            'message': message,
            'details': response.data
        }
    })

    response.data = serializer.data

    return response



