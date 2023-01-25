from datetime import datetime, timedelta

import mercadopago

from core.settings.base import MERCADO_PAGO_CONFIG, env

from db.models import Cart, CartItem

from .models import PaymentStrategy


class PaymentMethod:
    def __init__(self, cart: Cart = None, method: PaymentStrategy.PaymentStrategyInterface = None):
        if not cart:
            raise ValueError("PaymentMethod must be initialized with cart")

        if method:
            self._method = method(cart)
        else:
            self._method = MercadoPagoMethod(cart)

        self._cart = cart

    def get_preference(self):
        """
        Gets preference from current Payment State
        """
        preference = self._method.get_preference()

        return preference

    def get_payment_method(self):
        return self._method

    def change_payment_method(self, method: PaymentStrategy.PaymentStrategyInterface):
        """
        Changes current method
        """

        self._method = method(self._cart)


class MercadoPagoMethod(PaymentStrategy.PaymentStrategyInterface):
    """
    Payment method state of mercado pago
    """

    def __init__(self, cart: Cart):
        self._cart: Cart = cart

    def __str__(self):
        return "MercadoPago Payment Method"

    def format_preference(self, data):
        """
        Formats obtained preference
        """
        format_data = {
            "id": data["id"],
            "client_id": data["client_id"],
            "date_created": data["date_created"],
            "marketplace": data["marketplace"],
            "items": data["items"],
            "payer": data["payer"],
            "date_of_expiration": data["date_of_expiration"],
            "init_point": data["init_point"],
        }

        return format_data

    def format_cart_item(self, item: CartItem):
        """
        Formats cart item for preference data
        """
        format_data = {
            "id": item.product.id,
            "currency_id": "ARS",
            "description": item.product.description,
            "category_id": item.product.category.title,
            "picture_url": item.product.images[0],
            "title": item.product.title,
            "quantity": item.count,
            "unit_price": float(item.product.price),
        }

        return format_data

    def get_expiration_date(self, timedelta):
        """
        Gets expiration date using entered timedelta
        """
        return (datetime.now() + timedelta).strftime("%Y-%m-%dT%H:%M:%S-04:00")

    def get_preference(self):
        """
        Gets Mercado Pago preference data
        """
        cart_items = [self.format_cart_item(item) for item in self._cart.get_products()]

        user = self._cart.user

        sdk = mercadopago.SDK(MERCADO_PAGO_CONFIG["ACCESS_TOKEN"])

        preference_data = {
            "items": cart_items,
            "payer": {
                "name": user.first_name,
                "surname": user.last_name,
                "email": user.email,
                'identification': {'number': str(user.id)}
            },
            "binary_mode": MERCADO_PAGO_CONFIG.get("BINARY_MODE", True),
            "statement_descriptor": env("APP_NAME"),
            "back_urls": MERCADO_PAGO_CONFIG.get("BACK_URLS", {}),
            "date_of_expiration": self.get_expiration_date(
                MERCADO_PAGO_CONFIG.get("DATE_OF_EXPIRATION", timedelta(days=3))),
            "notification_url": MERCADO_PAGO_CONFIG.get("NOTIFICATION_URL",
                                                        "https://crudcrud.com/api/5ec933f740654c5fa42a209d53768460/payments"),
        }

        preference_response = sdk.preference().create(preference_data)

        preference = preference_response["response"]

        return self.format_preference(preference)
