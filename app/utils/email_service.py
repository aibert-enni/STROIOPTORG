import logging
import time

from django.conf import settings
from django.core.mail import EmailMessage

from apps.users.tasks import send_email

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.celery_available = True
        self.last_failure_time = None
        self.recovery_timeout = 60  # seconds

    def _check_celery_availability(self):
        if settings.DEBUG:
            return False

        if self.last_failure_time is None:
            return True
        if time.time() - self.last_failure_time > self.recovery_timeout:
            self.celery_available = True
            self.last_failure_time = None
        return self.celery_available

    def send_verification_email(self, subject, body, from_email, to_email, headers=None):
        """
        Try to send email via Celery, fallback to synchronous sending
        """
        if self._check_celery_availability():
            try:
                # Try async first
                send_email.delay(subject, body, from_email, to_email, headers)
                return {
                    'success': True,
                    'message': 'Registration successful! Please check your email for verification link.',
                    'method': 'async'
                }
            except Exception as e:
                logger.warning(f"Celery/Redis unavailable: {e}")
                self.celery_available = False

        # Fallback to synchronous email sending
        try:
            self._send_email_sync(subject, body, from_email, to_email, headers=None)
            return {
                'success': True,
                'message': 'Registration successful! Please check your email for verification link.',
                'method': 'sync'
            }
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {
                'success': False,
                'message': 'Registration completed but email delivery failed. Please contact support.',
                'method': 'failed'
            }

    def _send_email_sync(self, subject, body, from_email, to_email, headers=None):
        """Synchronous email sending"""
        msg = EmailMessage(
            subject, body, from_email, to_email, headers=headers
        )
        msg.content_subtype = "html"
        msg.send()


email_service = EmailService()