import logging

from allauth.account import app_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.request import Request

from utils.email_service import email_service

logger = logging.getLogger(__name__)

class AnonymousRequiredMixin:
    """Mixin для проверки, что пользователь не аутентифицирован."""
    redirect_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)

class CustomAccountAdapter(DefaultAccountAdapter):

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        try:
            EmailConfirmation(email_address=emailconfirmation.email_address, key=emailconfirmation.key).save()
        except Exception as e:
            logger.error(e)
            return
        ctx = {
            "user": emailconfirmation.email_address.user,
        }
        if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            ctx.update({"code": emailconfirmation.key})
        else:
            ctx.update(
                {
                    "key": emailconfirmation.key,
                    "activate_url": self.get_email_confirmation_url(
                        request, emailconfirmation
                    ),
                }
            )
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx, request)

    def send_mail(self, template_prefix: str, email: str, context: dict, request: Request = None) -> None:
        if request:
            current_site = get_current_site(request)
        else:
            current_site = None

        ctx = {
            "request": request,
            "email": email,
            "current_site": current_site,
        }

        password_reset_url = context.get("password_reset_url", None)

        if password_reset_url:
            context["password_reset_url"] = settings.FRONTEND_URL + settings.PASSWORD_RESET_CONFIRM_URL + context["uid"] + "/" + context["token"]

        activate_url = context.get("activate_url", None)

        if activate_url:
            context["activate_url"] = settings.FRONTEND_URL + settings.REGISTER_CONFIRM_REDIRECT_URL + context.get("key")

        ctx.update(context)
        msg = self.render_mail(template_prefix, email, ctx)

        email_service.send_verification_email(msg.subject, msg.body, msg.from_email, msg.to, None)
