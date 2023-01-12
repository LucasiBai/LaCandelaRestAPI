import mercadopago

from .models import PaymentState

from db.models import Cart

from .meta import MP_ACCESS_TOKEN


class PaymentMethod:
    def __init__(self, cart: Cart = None, state: PaymentState.PaymentStateInterface = None):
        if not cart:
            raise ValueError("PaymentMethod must be initialized with cart")

        if state:
            self._state = state(cart)
        else:
            self._state = MercadoPagoMethod(cart)

        self._cart = cart

    def get_preference(self):
        """
        Gets preference from current Payment State
        """
        preference = self._state.get_preference()

        return preference

    def get_payment_method(self):
        return self._state

    def change_payment_method(self, state: PaymentState.PaymentStateInterface):
        """
        Changes current method
        """

        self._state = state(self._cart)


class MercadoPagoMethod(PaymentState.PaymentStateInterface):
    """
    Payment method state of mercado pago
    """

    def __init__(self, cart: Cart):
        self._cart: Cart = cart

    def __str__(self):
        return "MercadoPago Payment Method"

    def get_preference(self):
        """Gets Mercado Pago preference data"""

        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

        preference_data = {
            "items": [
                {
                    "title": "Mi producto",
                    "quantity": 1,
                    "unit_price": 75.76,
                }
            ]
        }

        preference_response = sdk.preference().create(preference_data)

        preference = preference_response["response"]

        return preference

# example_data = {'additional_info': '', 'auto_return': '', 'back_urls': {'failure': '', 'pending': '', 'success': ''},
#                 'binary_mode': False, 'client_id': '4717115773333598', 'collector_id': 643565524, 'coupon_code': None,
#                 'coupon_labels': None, 'date_created': '2023-01-12T06:10:24.102-04:00', 'date_of_expiration': None,
#                 'expiration_date_from': None, 'expiration_date_to': None, 'expires': False, 'external_reference': '',
#                 'id': '643565524-83578599-1952-4a2e-a8b4-f481c1a97df5',
#                 'init_point': 'https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=643565524-83578599-1952-4a2e-a8b4-f481c1a97df5',
#                 'internal_metadata': None, 'items': [
#         {'id': '', 'category_id': '', 'currency_id': 'ARS', 'description': '', 'title': 'Mi producto', 'quantity': 1,
#          'unit_price': 75.76}], 'marketplace': 'MP-MKT-4717115773333598', 'marketplace_fee': 0, 'metadata': {},
#                 'notification_url': None, 'operation_type': 'regular_payment',
#                 'payer': {'phone': {'area_code': '', 'number': ''},
#                           'address': {'zip_code': '', 'street_name': '',
#                                       'street_number': None},
#                           'email': '',
#                           'identification': {'number': '', 'type': ''},
#                           'name': '', 'surname': '',
#                           'date_created': None, 'last_purchase': None},
#                 'payment_methods': {'default_card_id': None, 'default_payment_method_id': None,
#                                     'excluded_payment_methods': [{'id': ''}], 'excluded_payment_types': [{'id': ''}],
#                                     'installments': None, 'default_installments': None}, 'processing_modes': None,
#                 'product_id': None,
#                 'redirect_urls': {'failure': '', 'pending': '', 'success': ''},
#                 'sandbox_init_point': 'https://sandbox.mercadopago.com.ar/checkout/v1/redirect?pref_id=643565524-83578599-1952-4a2e-a8b4-f481c1a97df5',
#                 'site_id': 'MLA', 'shipments': {'default_shipping_method': None,
#                                                 'receiver_address': {'zip_code': '', 'street_name': '',
#                                                                      'street_number': None,
#                                                                      'floor': '', 'apartment': '', 'city_name': None,
#                                                                      'state_name': None, 'country_name': None}},
#                 'total_amount': None,
#                 'last_updated': None}
