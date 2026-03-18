# dashboard/utils/notifications.py
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_email_notification(recipient, subject, message, from_email=None):
    """Send email notification"""
    try:
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings,
                                                                'DEFAULT_FROM_EMAIL') else 'webmaster@localhost'

        send_mail(
            subject,
            message,
            from_email,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        return False