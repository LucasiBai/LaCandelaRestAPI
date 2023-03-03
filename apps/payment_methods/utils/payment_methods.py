from datetime import datetime, timedelta

from core.settings.base import MERCADO_PAGO_CONFIG, env

from db.models import Cart, CartItem, ShippingInfo

from apps.payment_methods.utils.services.mp_service import MPService

from apps.payment_methods.utils.models import payment_strategy


class PaymentMethod:
    def __init__(self, cart: Cart = None, method: payment_strategy.PaymentStrategyInterface = None):
        if not cart:
            raise ValueError("PaymentMethod must be initialized with cart")

        if method:
            self.__method = method(cart)
        else:
            self.__method = MercadoPagoMethod(cart)

        self.__cart = cart

    def get_preference(self):
        """
        Gets preference from current Payment State
        """
        preference = self.__method.get_preference()

        return preference

    def get_payment_method(self):
        return self.__method

    def change_payment_method(self, method: payment_strategy.PaymentStrategyInterface):
        """
        Changes current method
        """

        self._method = method(self.__cart)


class MercadoPagoMethod(payment_strategy.PaymentStrategyInterface):
    """
    Payment method state of mercado pago
    """
    service = MPService()

    def __init__(self, cart: Cart):
        self.__cart: Cart = cart

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
            "total_price": data["total_price"]
        }

        return format_data

    def format_cart_item(self, item: CartItem):
        """
        Formats cart item for preference data
        """
        product = item.product
        product.refresh_from_db()

        if product.stock < item.count:
            item.update_item_count()

            return ValueError

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
        cart_items = [self.format_cart_item(item) for item in self.__cart.get_products()]

        if ValueError in cart_items:
            raise ValueError("Item has insufficient stock.")

        user = self.__cart.user
        ship_info = ShippingInfo.objects.get_selected_shipping_info(user=user)

        preference_data = {
            "items": cart_items,
            "shipments": {
                "cost": float(ship_info.ship_price),
                "mode": "not_specified",
            },
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
            "notification_url": MERCADO_PAGO_CONFIG.get("NOTIFICATION_URL", None),
        }

        preference_response = self.service.get_preference(preference_data)

        preference = preference_response["response"]

        return self.format_preference(
            {**preference, "total_price": self.__cart.get_total_price() + ship_info.ship_price})
