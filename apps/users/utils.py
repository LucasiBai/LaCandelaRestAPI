from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail

from core.settings import base

FRONT_END_URL = base.env("FRONT_END_URL")
APP_NAME = base.env("APP_NAME")


def get_reset_password_url(email):
    """
    Generates user reset password url
    """
    user = get_user_model().objects.get(email=email)

    encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)

    reset_url = f"{FRONT_END_URL}/{encoded_pk}/{token}/"

    return reset_url


def send_reset_password_url_to(email):
    """
    Sends an email for a user with the reset password url
    """

    RESET_URL = get_reset_password_url(email)

    subject = f"Password reset from {APP_NAME}"

    message = f"The password reset link is as follows: {RESET_URL}"

    email_from = base.EMAIL_HOST_USER

    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)
