from .models.sender_strategy import SenderStrategyInterface

from .services.email_service import EmailService


class MessageSender:
    def __init__(self, sender: SenderStrategyInterface = None):
        if not sender:
            self.__sender = EmailSenderStrategy()
        else:
            self.__sender = sender()

    def get_sender(self):
        """
        Returns sender method
        """
        return self.__sender

    def send_message(self, message: str, **kwargs):
        """
        Sends message in current sender
        """
        return self.__sender.send_message(message=message, **kwargs)

    def change_sender(self, sender: SenderStrategyInterface = None):
        """
        Changes current sender to the entered

        Args:
            sender(SenderStrategyInterface): New sender
        """
        if not sender:
            raise ValueError("Method is missing 'sender' param.")

        self.__sender = sender()


class EmailSenderStrategy(SenderStrategyInterface):
    """
    Email sender strategy
    """

    def __str__(self):
        return "Email Sender Strategy"

    def send_message(self, subject: str = None, message: str = None, full_name_from: str = None, email_from: str = None,
                     recipient_email: str = None):
        if not all(isinstance(param, str) for param in (subject, message, full_name_from, email_from, recipient_email)):
            raise ValueError("Entered params must be strings.")

        return EmailService.send_email_to(**{
            "subject": f"{subject} from {email_from}",
            "message": f"{full_name_from} says:\n {message}",
            "email_from": recipient_email,
            "recipient_email": recipient_email})
