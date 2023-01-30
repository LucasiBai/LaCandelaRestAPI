from django.test import TestCase

from apps.payment_methods.utils.services.mp_service import MPService


class MPServiceTests(TestCase):
    """
    Tests Mp service
    """

    def setUp(self):
        self.service = MPService()

    def test_get_preference_successful(self):
        """
        Tests if service has get preference method
        """

        preference_data = {
            "items": [{
                "id": "item-ID-1234",
                "title": "Mi producto",
                "currency_id": "ARS",
                "picture_url": "https://www.mercadopago.com/org-img/MP3/home/logomp3.gif",
                "description": "Descripción del Item",
                "category_id": "art",
                "quantity": 1,
                "unit_price": 75.76
            }],
            "payer": {
                "name": "Juan",
                "surname": "Lopez",
                "email": "user@email.com",
                "phone": {
                    "area_code": "11",
                    "number": "4444-4444"
                },
                "identification": {
                    "type": "DNI",
                    "number": "12345678"
                },
                "address": {
                    "street_name": "Street",
                    "street_number": 123,
                    "zip_code": "5700"
                }
            },
        }

        preference_response = self.service.get_preference(preference_data)

        preference = preference_response["response"]

        self.assertTrue(preference)
        self.assertTrue(preference["init_point"])

        self.assertEqual(preference_data["items"][0]["id"], preference["items"][0]["id"])
        self.assertEqual(preference_data["payer"]["identification"]["number"],
                         preference["payer"]["identification"]["number"])

    def test_check_payment_successful(self):
        """
        Tests if check_payment method returns true if payment was approved
        """
        pay_id = 1311430300

        check_payment = self.service.check_payment(pay_id)

        self.assertTrue(check_payment)

    # TODO : Test No approved payment

    # TODO : Test No existing payment
