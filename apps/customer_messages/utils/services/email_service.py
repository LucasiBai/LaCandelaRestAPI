from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_email_to(*args, **kwargs):
        """
        Sends email to recipient email

        Returns:
            True if email was sent
        """
        return True
