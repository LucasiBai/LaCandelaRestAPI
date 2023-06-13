from .models.sender_strategy import SenderStrategyInterface


class MessageSender:
    def __init__(self, sender: SenderStrategyInterface = None):
        if not sender:
            self.__sender = EmailSenderStrategy()
        else:
            self.__sender = sender()

    def get_sender(self):
        """
        Returns send method
        """
        return self.__sender

    def send_message(self, message: str):
        """
        Sends message in current sender
        """
        return self.__sender.send_message(message)


class EmailSenderStrategy(SenderStrategyInterface):
    """
    Email sender strategy
    """

    def __str__(self):
        return "Email Sender Strategy"

    def send_message(self, message):
        return message
