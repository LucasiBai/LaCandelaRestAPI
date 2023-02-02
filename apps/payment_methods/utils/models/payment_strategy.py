from abc import ABC, abstractmethod

from db.models import Cart


class PaymentStrategyInterface(ABC):
    """
    Payment State abstract method
    """

    @abstractmethod
    def __init__(self, cart: Cart):
        self.__cart: Cart = cart

    @abstractmethod
    def get_preference(self):
        """Gets preference of payment method"""
