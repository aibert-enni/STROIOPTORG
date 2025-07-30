from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import PasswordChangeSerializer, \
    ProfileCreateSerializer, UserFirstnameSuccessResponseSerializer, \
    UserFirstnameDataSerializer, ProfileSuccessResponseSerializer, ProfileDataSerializer
from utils.serializers import ErrorSerializer, SuccessResponseSerializer


class AccountMyAccountTemplateView(TemplateView):
    template_name = 'users/account/account-my.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'my_account'
        return context_data


class AccountOrdersTemplateView(TemplateView):
    template_name = 'users/account/account-orders.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'orders'
        return context_data


class AccountOrderTemplateView(TemplateView):
    template_name = 'users/account/account-order.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'orders'
        return context_data


class AccountProfileEditTemplateView(TemplateView):
    template_name = 'users/account/account-profile-edit.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'profile-edit'
        return context_data


class AccountDeliveryAddressTemplateView(TemplateView):
    template_name = 'users/account/account-delivery-address.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'delivery-address'
        return context_data


class AccountDeliveryAddressCreateTemplateView(TemplateView):
    template_name = 'users/account/account-delivery-address-create.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'delivery-address'
        return context_data


class AccountDeliveryAddressEditTemplateView(TemplateView):
    template_name = 'users/account/account-delivery-address-edit.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'delivery-address'
        return context_data


class AccountPasswordChangeTemplateView(TemplateView):
    template_name = 'users/account/account-password-change.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['account_page'] = 'password'
        return context_data


class GetUserFirstnameAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        operation_id='get_user_firstname',
        tags=['profile'],
        summary='Получить имя пользователя',
        description='Получаем имя пользователя',
        responses={
            200: UserFirstnameSuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа для получения имя данного пользователя',
                value={
                    'status': 'success',
                    'message': '',
                    'data': {
                        'firstname': 'Jeka'
                    }
                },
                request_only=True
            )
        ]
    )
    def get(self, request):
        firstname = request.user.firstname

        data_serializer = UserFirstnameDataSerializer({'firstname': firstname})

        return Response({
            'status': 'success',
            'message': 'Имя получено',
            'data': data_serializer.data
        })


class ProfileAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        operation_id='get_user_profile',
        tags=['profile'],
        summary='Получить данные профиля данного пользователя',
        description='Получаем данные профиля данного пользователя',
        responses={
            200: ProfileSuccessResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа для получения профиля',
                value={
                    'status': 'success',
                    'message': '',
                    'data': {
                        "email": "admin@gmail.com",
                        "phone_number": "8777231342",
                        "region": None,
                        "firstname": "Chukcha",
                        "lastname": "Poka"
                    }
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        serializer = ProfileDataSerializer(request.user)

        return Response({
            'status': 'success',
            'message': 'Профиль получен',
            'data': serializer.data
        })

    @extend_schema(
        operation_id='get_user_profile',
        tags=['profile'],
        summary='Изменить данные профиля данного пользователя',
        description='Изменить данные профиля данного пользователя',
        request=ProfileCreateSerializer,
        responses={
            200: ProfileSuccessResponseSerializer,
            400: ErrorSerializer
        },
        examples=[
            OpenApiExample(
                'Тело для изменения профиля',
                summary='Тело для изменения профиля',
                description='Пример тела запроса при изменении профиля',
                value={
                    "email": "user@example.com",
                    "phone_number": "130823934099",
                    "region": 1,
                    "firstname": "Habib",
                    "lastname": "Nurmagamedov"
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример ответа',
                summary='Пример ответа',
                description='Пример ответа для изменения профиля',
                value={
                    "status": "success",
                    "message": "Профиль обновлен",
                    "data": {
                        "email": "admin@gmail.com",
                        "phone_number": "8777231342",
                        "region": None,
                        "firstname": "Chukcha",
                        "lastname": "Poka"
                    }

                },
                response_only=True
            )
        ]
    )
    def put(self, request):
        serializer = ProfileCreateSerializer(request.user, data=request.data)

        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        data_serializer = ProfileDataSerializer(profile)
        return Response({
            'status': 'success',
            'message': 'Профиль обновлен',
            'data': data_serializer.data
        })


class PasswordChangeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        operation_id='change_password',
        tags=['profile'],
        summary='Изменить пароль авторизованному пользователю',
        description='Изменить пароль авторизованному пользователю',
        request=PasswordChangeSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorSerializer
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'user': request.user})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={
            'status': 'success',
            'message': 'Пароль обновлен удачно'
        }, status=status.HTTP_200_OK)
