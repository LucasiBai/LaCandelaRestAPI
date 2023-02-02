from .models import order_strategy


class OrderCreation:
    def __init__(self, method: order_strategy.OrderStrategyInterface = None):
        if method:
            self.__method = method()
        else:
            self.__method = MercadoPagoMethod()

    def get_response(self):
        """
        Gets response from current order strategy
        """
        response = self.__method.get_response()

        return response

    def get_order_method(self):
        return self.__method

    def change_order_method(self, method: order_strategy.OrderStrategyInterface):
        """
        Changes current method
        """

        self.__method = method()


class MercadoPagoMethod(order_strategy.OrderStrategyInterface):
    """
    Order creation strategy for OrderCreation
    """

    def __str__(self):
        return "Mercado Pago Order Creation Method"

    def get_response(self, data):
        """
        Creates order response with mp payment
        """
        return "response"
