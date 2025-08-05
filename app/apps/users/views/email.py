from allauth.account.models import get_emailconfirmation_model
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.serializers import ErrorResponseSerializer, SuccessResponseSerializer


class ConfirmEmailTemplateView(TemplateView):
    template_name = "users/auth/email/confirm_email.html"

class PasswordResetTemplateView(TemplateView):
    template_name = "users/auth/password_reset/password_reset.html"

class PasswordResetConfirmView(TemplateView):
    template_name = "users/auth/password_reset/password_reset_confirm.html"

class RegisterConfirmView(TemplateView):
    template_name = "users/auth/email/confirm_email.html"

class CustomConfirmEmailAPIView(APIView):

    @extend_schema(
        operation_id='confirm_email',
        summary='Подтвердить почту',
        description='Подтвердить почту',
        responses={
            200: SuccessResponseSerializer(),
            400: ErrorResponseSerializer(),
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа при подтверждении почты',
                value={
                    'status': 'success',
                    "message": "Почта admin@gmail.com удачно подтверждена!",
                },
                response_only=True
            ),
            OpenApiExample(
                'Ошибка 400',
                summary='Ссылка невалидна или истек срок действия',
                description='Пример ответа, когда ссылка невалидна или истек срок действия',
                value={
                    "error": {
                        "code": "validation_error",
                        "message": "Ссылка невалидна или истек срок действия",
                        "details": {
                            "detail": "Ссылка невалидна или истек срок действия"
                        }
                    }
                },
                response_only=True,
                status_codes=["400"]
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        key = self.kwargs["key"]

        model = get_emailconfirmation_model()
        emailconfirmation = model.from_key(key)

        if not emailconfirmation or emailconfirmation.email_address.verified:
            raise ValidationError("Ссылка невалидна или истек срок действия")

        emailconfirmation.email_address.verified = True
        emailconfirmation.email_address.save()

        return Response({
            'status': 'success',
            'message': f'Почта {emailconfirmation.email_address} удачно подтверждена!',
        })

