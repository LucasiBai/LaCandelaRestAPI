from rest_framework.response import Response
from rest_framework import status

from .models import order_strategy
from .services.mp_service import MPService

from db.models import Order


class OrderCreation:
    def __init__(self, method: order_strategy.OrderStrategyInterface = None):
        if method:
            self.__method = method()
        else:
            self.__method = MercadoPagoMethod()

    def get_response(self, data):
        """
        Gets response from current order strategy
        """
        response = self.__method.get_response(data)

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

    def format_response_data(self, order: Order, **kwargs):
        """
        Formats response data with entered order

        Args:
            order(Order): order with data

        Returns:
            formatted data
        """
        response = {
            "user": {
                "id": order.buyer.id,
                "email": order.buyer.email
            }
        }

        return response

    def get_response(self, data):
        """
        Creates order response with mp payment
        """
        topic = data.get("topic", None)

        if topic == "merchant_order":
            return Response(status=status.HTTP_200_OK)

        pay_id = data.get("data", {"id": None})["id"]

        service = MPService()

        try:
            is_approved, data = service.check_payment(pay_id)

            if is_approved:
                order = service.create_order(data)

                res_data = self.format_response_data(order)

                return Response(res_data, status=status.HTTP_200_OK)

        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
