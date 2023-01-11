class PaymentMethods:

    @staticmethod
    def get_mp_preference(self, cart):
        """Gets Mercado Pago preference data"""
        # TODO: add functionality

# from core.settings import base
#
# import mercadopago
#
# MP_ACCESS_TOKEN = base.env("MP_ACCESS_TOKEN")
# MP_ACCESS_TOKEN = "TEST-4717115773333598-011110-769fe468dbdfff9d1d6a6e38bd969faa-643565524"
#
# sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
#
# preference_data = {
#     "items": [
#         {
#             "title": "Mi producto",
#             "quantity": 1,
#             "unit_price": 75.76,
#         }
#     ]
# }
#
# preference_response = sdk.preference().create(preference_data)
# preference = preference_response["response"]
#
