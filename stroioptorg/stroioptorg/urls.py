from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path, reverse

from apps.users.views.auth import GoogleLogin, GoogleLoginCallback
from apps.users.views.email import CustomConfirmEmailAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.main.urls', namespace='main')),
    path('', include('apps.users.urls', namespace='users')),
    path('', include('apps.product.urls', namespace='product')),
    path('', include('apps.order.urls', namespace='order')),
    path('', include('apps.wishlist.urls', namespace='wishlist')),

    # auth
    path('api/v1/auth/', include('apps.users.api-urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    re_path(
        r'^api/v1/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        CustomConfirmEmailAPIView.as_view(),
        name='account_confirm_email'
    ),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),

    # google auth
    path('api/v1/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path(
        "api/v1/auth/google/callback/",
        GoogleLoginCallback.as_view(),
        name="google_login_callback",
    ),

    # api v1
    path('api/v1/', include('apps.product.api_urls', namespace='api-product')),
    path('api/v1/', include('apps.order.api_urls', namespace='api-order')),
    path('api/v1/', include('apps.wishlist.api_urls', namespace='api-wishlist')),
    # path('api/v1/', include('apps.review.api_urls', namespace='api-review')),
    path('api/v1/', include('apps.health.api_urls', namespace='api-health')),
]

if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
    from django.conf.urls.static import static

    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
        path('silk/', include('silk.urls', namespace='silk')),
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
