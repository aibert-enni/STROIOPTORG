from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Region, City, Address
from apps.users.serializers import CreateAddressSerializer, RegionSuccessResponseSerializer, RegionDataSerializer, \
    CitySuccessResponseSerializer, CityDataSerializer, AddressSuccessResponseSerializer, AddressDataSerializer
from utils.serializers import ErrorResponseSerializer


class GetRegionListView(APIView):

    @extend_schema(
        operation_id='get_regions_list',
        summary='Получить список всех регионов',
        description='Возвращает список всех доступных регионов в системе',
        tags=['address'],
        responses={
            200: RegionSuccessResponseSerializer(),
        }
    )
    def get(self, request):
        regions = Region.objects.all()
        serializer = RegionDataSerializer(regions, many=True)

        return Response({
            'status': 'success',
            'message': 'Список регионов получен',
            'data': serializer.data,
        })


class GetCitiesListView(APIView):

    @extend_schema(
        operation_id='get_cities_list',
        summary='Получить список всех городов',
        description='Возвращает список всех доступных городов в системе',
        tags=['address'],
        responses={
            200: CitySuccessResponseSerializer(),
        },
    )
    def get(self, request):
        cities = City.objects.all()
        serializer = CityDataSerializer(cities, many=True)
        return Response({
            'status': 'success',
            'message': 'Список городов получен',
            'data': serializer.data,
        })


class UserDeliveryAddress(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        operation_id='get_user_delivery_address',
        summary='Получить адрес данного пользователя',
        description='Возвращает адрес данного пользователя',
        tags=['user delivery address'],
        responses={
            200: AddressSuccessResponseSerializer(),
            404: ErrorResponseSerializer(),
        },
        examples=[
            OpenApiExample(
                'Ошибка 404',
                summary='Пользователь не найден',
                description='Пример ответа, когда пользователь или адрес не найден',
                value={
                    "error": {
                        "code": "http404",
                        "message": "No Address matches the given query.",
                        "details": {
                            "detail": "No Address matches the given query."
                        }
                    }
                },
                response_only=True,
                status_codes=["404"]
            )
        ]
    )
    def get(self, request):
        address = get_object_or_404(Address, user=request.user)
        data_serializer = AddressDataSerializer(address,
                                       context={'phone_number': request.user.phone_number, 'email': request.user.email})
        return Response({
            'status': 'success',
            'message': 'Адрес получен',
            'data': data_serializer.data,
        })

    @extend_schema(
        operation_id='create_user_delivery_address',
        summary='Создать адрес доставки данного пользователя',
        description='Позволяет создать новый адрес доставки для данного пользователя.',
        tags=['user delivery address'],
        request=CreateAddressSerializer,
        responses={
            201: AddressSuccessResponseSerializer,
            400: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Тело для создания адреса доставки',
                summary='Тело для создания адреса доставки',
                description='Пример тела запроса при создании нового адреса адреса доставки',
                value={
                    "firstname": "George",
                    "lastname": "Verstappen",
                    "company": "Slipknot",
                    "street": "west cost 1",
                    "house_number": "56",
                    "city": 1
                },
                request_only=True
            ),
            OpenApiExample(
                'Ошибка валидации',
                summary='Ошибка: неверные данные',
                description='Пример ответа, если переданы некорректные данные',
                value={
                    "error": {
                        "code": "validation_error",
                        "message": "Ошибка валидации данных.",
                        "details": {
                            "firstname": ["Это поле обязательно."],
                            "city": ["Такого города не существует"]
                        }
                    }
                },
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                'Адрес уже существует',
                summary='Ошибка: адрес уже добавлен',
                description='Возвращается, если у пользователя уже есть такой адрес',
                value={
                    "error": {
                        "code": "validationerror",
                        "message": "Invalid input.",
                        "details": {
                            "user": "Адрес у пользователя уже существует"
                        }
                    }
                },
                response_only=True,
                status_codes=["400"]
            )
        ]
    )
    def post(self, request):
        serializer = CreateAddressSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        try:
            address = serializer.save()
        except IntegrityError:
            raise ValidationError({
                'user': 'Адрес у пользователя уже существует'
            })
        data_serializer = AddressDataSerializer(address, context={'email': request.user.email,
                                                                  'phone_number': request.user.phone_number})
        return Response({
            'status': 'success',
            'message': 'Адрес создан',
            'data': data_serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id='put_user_delivery_address',
        summary='Изменить адрес доставки данного пользователя',
        description='Позволяет изменить адрес доставки данного пользователя',
        tags=['user delivery address'],
        request=CreateAddressSerializer,
        responses={
            201: AddressSuccessResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                'Тело для изменения адреса доставки',
                summary='Тело для изменения адреса доставки',
                description='Пример тела запроса при изменении адреса адреса доставки',
                value={
                    "firstname": "George",
                    "lastname": "Verstappen",
                    "company": "Slipknot",
                    "street": "west cost 1",
                    "house_number": "56",
                    "city": 1
                },
                request_only=True
            ),
            OpenApiExample(
                'Ошибка валидации',
                summary='Ошибка: неверные данные',
                description='Пример ответа, если переданы некорректные данные',
                value={
                    "error": {
                        "code": "validation_error",
                        "message": "Ошибка валидации данных.",
                        "details": {
                            "firstname": ["Это поле обязательно."],
                            "city": ["Такого города не существует"]
                        }
                    }
                },
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                'Ошибка 404',
                summary='Адрес не найден',
                description='Пример ответа, когда адрес не найден',
                value={
                    "error": {
                        "code": "http404",
                        "message": "No Address matches the given query.",
                        "details": {
                            "detail": "No Address matches the given query."
                        }
                    }
                },
                response_only=True,
                status_codes=["404"]
            )
        ]
    )
    def put(self, request):
        address = get_object_or_404(Address, user=request.user)
        serializer = CreateAddressSerializer(address, data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        data_serializer = AddressDataSerializer(address, context={'email': request.user.email, 'phone_number': request.user.phone_number})
        return Response({
            'status': 'success',
            'message': '',
            'data': data_serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id='delete_user_delivery_address',
        summary='Удалить адрес данного пользователя',
        description='Удаляет адрес данного пользователя',
        tags=['user delivery address'],
        responses={
            404: ErrorResponseSerializer(),
        },
        examples=[
            OpenApiExample(
                'Ошибка 404',
                summary='Адрес не найден',
                description='Пример ответа, когда адрес не найден',
                value={
                    "error": {
                        "code": "http404",
                        "message": "No Address matches the given query.",
                        "details": {
                            "detail": "No Address matches the given query."
                        }
                    }
                },
                response_only=True,
                status_codes=["404"]
            )
        ]
    )
    def delete(self, request):
        address = get_object_or_404(Address, user=request.user)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
