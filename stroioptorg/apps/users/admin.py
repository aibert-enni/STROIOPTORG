from django.contrib import admin

from apps.users.models import User, Region, City, Address, Country

# Register your models here.
admin.site.register(User)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(Address)
admin.site.register(Country)