from django.urls import path

from apps.users.views import GetRegionListView
from apps.users.views.account import GetUserFirstnameAPIView, ProfileAPIView, PasswordChangeAPIView
from apps.users.views.address import UserDeliveryAddress, GetCitiesListView

app_name = 'users-api'

urlpatterns = [
    path('user/firstname/', GetUserFirstnameAPIView.as_view(), name='user-firstname'),
    path('user/profile/', ProfileAPIView.as_view(), name='user-profile'),
    path('user/address/me/', UserDeliveryAddress.as_view(), name='user-address'),

    # address
    path('address/regions/', GetRegionListView.as_view(), name='user-regions'),
    path('address/cities/', GetCitiesListView.as_view(), name='user-cities'),

    # password
    path('password/change/', PasswordChangeAPIView.as_view(), name='user-change-password'),
]
