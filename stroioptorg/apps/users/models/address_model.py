from django.db import models

from apps.main.models import TimeStampedModel
from utils.validators import firstname_validator, lastname_validator


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название страны')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

class Region(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название региона')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='regions', verbose_name='Страна')

    def __str__(self):
        return f'{self.country} -> {self.name}'

    class Meta:
        unique_together = ('name', 'country')
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название города')
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='cities', verbose_name='Регион')

    def __str__(self):
        return f'{self.region} -> {self.name}'

    class Meta:
        unique_together = ('name', 'region')
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

class Address(TimeStampedModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='address', verbose_name='Пользователь')

    firstname = models.CharField(max_length=100, validators=[firstname_validator], verbose_name='Имя')
    lastname = models.CharField(max_length=100, validators=[lastname_validator], verbose_name='Фамилия')

    company = models.CharField(max_length=100, verbose_name='Название компании', blank=True, null=True)

    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='addresses', verbose_name='Город')
    street = models.CharField(max_length=255, verbose_name='Улица')
    house_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Номер квартиры')

    @property
    def region(self):
        return self.city.region

    @property
    def country(self):
        return self.region.country

    def __str__(self):
        return f"{self.street}, {self.city.name}, {self.region.name}, {self.country.name}"

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'