from django.views.generic import TemplateView


class AccountTemplateView(TemplateView):
    template_name = 'users/account.html'