from django.conf import settings
from django.views.generic import  TemplateView

from apps.users.utils import AnonymousRequiredMixin


class LoginView(TemplateView):
    template_name = 'users/auth/login.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['google_client_id'] = settings.GOOGLE_OAUTH_CLIENT_ID
        context_data['google_callback_uri'] = settings.GOOGLE_OAUTH_CALLBACK_URL
        return context_data