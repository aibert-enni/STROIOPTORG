from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import User, Region, Address, City
from utils.validators import firstname_validator, lastname_validator, phone_number_validator


class UserFirstnameSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=255)

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'region', 'firstname', 'lastname']

class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()

    def get_region(self, obj):
        return obj.city.region.id

    def get_full_address(self, obj):
        full_address = f'{obj.city.name}, {obj.country.name}, {obj.street}'
        if obj.house_number:
            full_address += f', кв.{obj.house_number}'
        return full_address

    def get_phone_number(self, obj):
        return self.context.get('phone_number')

    def get_email(self, obj):
        return self.context.get('email')

    class Meta:
        model = Address
        exclude = ['user', 'created_at', 'updated_at']

class CreateAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        exclude = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context.get('user')
        return Address.objects.create(user=user, **validated_data)

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id','name']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id','name', 'region_id']

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate_current_password(self, current_password):
        user = self.context.get('user')

        if not user.check_password(current_password):
            raise serializers.ValidationError('Текущий пароль неверный')

        return current_password

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError('Новые пароли не совпадают')

        validate_password(attrs['new_password1'], self.context['user'])

        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password1'])
        user.save()

        return user

class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        attrs['username'] = attrs.get('email')

        return super().validate(attrs)

class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(required=True)
    firstname = serializers.CharField(required=True, validators=[firstname_validator])
    lastname = serializers.CharField(required=True, validators=[lastname_validator])
    phone_number = serializers.CharField(required=True, validators=[phone_number_validator])


    def validate(self, attrs):
        attrs['username'] = attrs.get('email')

        return super().validate(attrs)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['firstname'] = self.validated_data.get('firstname', '')
        data['lastname'] = self.validated_data.get('lastname', '')
        data['phone_number'] = self.validated_data.get('phone_number', '')
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.firstname = self.cleaned_data.get('firstname')
        user.lastname = self.cleaned_data.get('lastname')
        user.phone_number = self.cleaned_data.get('phone_number')

        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except ValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
