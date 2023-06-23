from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_email_to(*args, **kwargs):
        """
        Sends email to recipient email

        Returns:
            True if email was sent
        """
        subject = kwargs.get("subject", None)
        message = kwargs.get("message", None)
        full_name_from = kwargs.get("full_name_from", None)
        email_from = kwargs.get("email_from", None)
        recipient_email = kwargs.get("recipient_email", None)

        if not (subject and message and full_name_from and email_from and recipient_email):
            raise ValueError(
                "send_email method must contain subject, message, full_name_from, email_from and recipient_email.")

        return True
