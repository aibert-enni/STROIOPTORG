from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import UserFirstnameSerializer, ProfileSerializer, PasswordChangeSerializer


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

    def get(self, request):
        firstname = request.user.firstname

        serializer = UserFirstnameSerializer({"firstname": firstname})

        return Response(serializer.data)


class ProfileAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = ProfileSerializer(request.user)

        return Response(serializer.data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class PasswordChangeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'user': request.user})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={
            'message': 'Пароль обновлен удачно',
        }, status=status.HTTP_200_OK)