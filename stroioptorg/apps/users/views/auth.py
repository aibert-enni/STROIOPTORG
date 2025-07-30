from urllib.parse import urljoin

import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.utils import jwt_encode
from django.conf import settings
from django.http import HttpResponseRedirect
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.users.models import User


class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,  # This is fix for incompatibility between django-allauth==65.3.1 and dj-rest-auth==7.0.1
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter,
            headers,
            basic_auth,
        )

class GoogleLogin(SocialLoginView): # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = CustomGoogleOAuth2Client


class GoogleLoginCallback(APIView):

    @extend_schema(
        operation_id='google_login_callback',
        summary='Колбэк для гугл авторизации',
        description='Колбэк для гугл авторизации',
        parameters=[
            OpenApiParameter(
                name='code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Google OAuth2 code'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):

        code = request.GET.get("code")

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token_endpoint_url = urljoin("http://localhost:8000", reverse("google_login"))
        backend_response = requests.post(url=token_endpoint_url, data={"code": code})

        if backend_response.status_code != 200:
            return Response({"detail": "Failed to get tokens"}, status=status.HTTP_400_BAD_REQUEST)

        token_data = backend_response.json()

        user_email = token_data["user"]["email"]

        try:
            user = User.objects.get(email=user_email)
            access_token, refresh_token = jwt_encode(user)
        except User.DoesNotExist:
            return Response({"detail": "Missing tokens"}, status=status.HTTP_400_BAD_REQUEST)


        if not access_token or not refresh_token:
            return Response({"detail": "Missing tokens"}, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponseRedirect(settings.FRONTEND_URL + settings.GOOGLE_AUTH_REDIRECT_URL)

        # Ставим куки
        set_jwt_cookies(response, access_token, refresh_token)

        return response