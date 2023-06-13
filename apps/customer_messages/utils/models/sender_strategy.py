from abc import ABC, abstractmethod


class SenderStrategyInterface(ABC):
    """
    Message Sender Strategy interface
    """

    @abstractmethod
    def send_message(self, subject: str, message: str, email_from: str, recipient_email: str):
        """Sends message in current sender"""
