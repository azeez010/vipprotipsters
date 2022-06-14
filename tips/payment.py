from django.urls import reverse
from django.views.generic import FormView, TemplateView
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class PaypalReturnView(TemplateView):
    template_name = 'paypal_success.html'

class PaypalCancelView(TemplateView):
    template_name = 'paypal_cancel.html'