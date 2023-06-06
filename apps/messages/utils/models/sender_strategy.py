from abc import ABC, abstractmethod


class SenderStrategyInterface(ABC):
    """
    Message Sender Strategy interface
    """

    @abstractmethod
    def send_message(self, message):
        """Sends message in current sender"""
