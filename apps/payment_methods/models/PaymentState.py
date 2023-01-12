from abc import ABC, abstractmethod

from db.models import Cart


class PaymentStateInterface(ABC):
    """
    Payment State abstract method
    """

    @abstractmethod
    def __init__(self, cart: Cart):
        self._cart: Cart = cart

    @abstractmethod
    def get_preference(self):
        """Gets preference of payment method"""
