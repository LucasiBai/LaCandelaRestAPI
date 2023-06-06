from .models.sender_strategy import SenderStrategyInterface


class MessageSender:
    def __init__(self, sender: SenderStrategyInterface):
        self.__sender = sender

    def get_sender(self):
        return self.__sender


class EmailSenderStrategy(SenderStrategyInterface):
    """
    Email sender strategy
    """

    def send_message(self, message):
        return message
