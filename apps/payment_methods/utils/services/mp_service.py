from django.contrib.auth import get_user_model

import mercadopago

from core.settings.base import MERCADO_PAGO_CONFIG

from db.models import Order, ShippingInfo


class MPService:
    """
    Mercado Pago Service
    """
    __instance = None
    sdk = mercadopago.SDK(MERCADO_PAGO_CONFIG["ACCESS_TOKEN"])

    def __new__(cls, *args, **kwargs):
        if not MPService.__instance:
            MPService.__instance = object.__new__(cls)
        return MPService.__instance

    def get_preference(self, pref_config: dict):
        """
        Gets preference of buy in mercado pago sdk

        Args:
            pref_config(dict): preference data config

        Returns:
            Obtained preference
        """

        preference: dict = self.sdk.preference().create(pref_config)

        return preference

    def check_payment(self, pay_id: int):
        """
        Checks if payment was done successfully

        Args:
            pay_id(int): payment id

        Returns:
            True if payment is approved or False otherwise
        """
        payment = self.sdk.payment().get(pay_id)

        status = payment.get("status", None)

        if status != 200:
            raise ValueError("Payment id do not exist.")

        return (payment["response"]["status"] == "approved", payment["response"])

    def create_order(self, data: dict):
        """
        Creates an order with entered data

        Args:
            data(dict): data with order data

        Returns:
            order created
        """
        payer_data = data.get("payer", None)

        user = get_user_model().objects.filter(email=payer_data["email"]).first()

        user_ship_info = ShippingInfo.objects.filter(user=user).last()

        products = data.get("additional_info", {"items": None})["items"]

        parsed_products = []
        for product in products:
            data = {
                "product": product["id"],
                "count": int(product["quantity"])
            }
            parsed_products.append(data)

        order = Order.objects.create(buyer=user, shipping_info=user_ship_info)
        order.save()

        order.create_order_products(parsed_products)

        return order
