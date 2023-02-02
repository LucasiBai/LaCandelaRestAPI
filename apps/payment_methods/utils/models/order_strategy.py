from abc import ABC, abstractmethod


class OrderStrategyInterface(ABC):
    """
    Order creation abstract method
    """

    @abstractmethod
    def get_response(self, data):
        """Gets response for API"""
