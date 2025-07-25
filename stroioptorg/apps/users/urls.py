from django.contrib.auth import views as auth_views
from django.urls import path

from apps.users.views import RegisterView, LoginView
from apps.users.views.email import PasswordResetTemplateView, PasswordResetConfirmView
from apps.users.views.account import AccountMyAccountTemplateView, AccountOrdersTemplateView, AccountOrderTemplateView, \
    AccountProfileEditTemplateView, AccountDeliveryAddressTemplateView, AccountDeliveryAddressEditTemplateView, \
    AccountDeliveryAddressCreateTemplateView, AccountPasswordChangeTemplateView

app_name = 'users'

urlpatterns = [
    # auth
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),

    # account
    path('account/', AccountMyAccountTemplateView.as_view(), name='account'),
    path('account/orders/', AccountOrdersTemplateView.as_view(), name='orders'),
    path('account/orders/<int:pk>/', AccountOrderTemplateView.as_view(), name='order'),
    path('account/profile/edit/', AccountProfileEditTemplateView.as_view(), name='profile-edit'),
    path('account/delivery-address/', AccountDeliveryAddressTemplateView.as_view(), name='delivery-address'),
    path('account/delivery-address/edit/', AccountDeliveryAddressEditTemplateView.as_view(), name='delivery-address-edit'),
    path('account/delivery-address/create/', AccountDeliveryAddressCreateTemplateView.as_view(), name='delivery-address-create'),
    path('account/password-change/', AccountPasswordChangeTemplateView.as_view(), name='password-change'),

    # reset password
    path('password_reset/', PasswordResetTemplateView.as_view(), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/auth/password_reset/password_reset_done.html'),
         name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/auth/password_reset/password_reset_complete.html'), name='password_reset_complete'),
]
