from django.urls import reverse
from django.views.generic import TemplateView


# Create your views here.
class HomeView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        print(reverse('api-order:stripe-webhook'))
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context