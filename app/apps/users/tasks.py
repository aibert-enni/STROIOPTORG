from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives


@shared_task
def send_email(subject, body, from_email, to, headers=None):
    msg = EmailMessage(
        subject, body, from_email, to, headers=headers
    )
    msg.content_subtype = "html"
    msg.send()

@shared_task
def send_emails(subject, body, from_email, to, headers=None):
    msg = EmailMultiAlternatives(
        subject, body, from_email, to, headers=headers
    )
    msg.content_subtype = "html"
    msg.send()