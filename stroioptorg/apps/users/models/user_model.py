from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import  PermissionsMixin
from django.db import models

from utils.validators import firstname_validator, lastname_validator, phone_number_validator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт и возвращает пользователя с email.
        """
        if not email:
            raise ValueError('Пользователю нужно указать email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создаёт и возвращает суперпользователя с email.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Создаём пользователя с полем email вместо username
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Почта')
    firstname = models.CharField(max_length=100, validators=[firstname_validator], verbose_name='Имя')
    lastname = models.CharField(max_length=100, validators=[lastname_validator], verbose_name='Фамилия')
    phone_number = models.CharField(max_length=15, unique=True, validators=[phone_number_validator], verbose_name='Номер телефона', null=True, blank=True)
    region = models.ForeignKey('users.Region', on_delete=models.SET_NULL, related_name='user', null=True, blank=True, verbose_name='Регион')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


    def __str__(self):
        return self.email
