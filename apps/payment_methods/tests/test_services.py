from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.payment_methods.utils.services.mp_service import MPService

from db.models import ShippingInfo, Product, Category


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

        check_payment, data = self.service.check_payment(pay_id)

        self.assertTrue(check_payment)
        self.assertTrue(data)

    def test_check_payment_rejected_payment_reject(self):
        """
        Tests if check_payment method returns false if payment was rejected
        """
        pay_id = 1312160969

        check_payment, data = self.service.check_payment(pay_id)

        self.assertFalse(check_payment)
        self.assertTrue(data)

    def test_check_payment_no_existing_payment_reject(self):
        """
        Tests if check_payment method raise an error with no existing payment
        """
        pay_id = 41235521

        with self.assertRaises(ValueError):
            self.service.check_payment(pay_id)

    def test_create_order_successful(self):
        """
        Tests if service can create an order with pay data
        """
        # Create product
        category = Category.objects.create(title="TestCategory")

        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 11,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Create user and shipping info
        user = get_user_model().objects.create_user(email="testemail@test.com")

        mock_user_shipping_info = {
            "user": user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        ShippingInfo.objects.create(**mock_user_shipping_info)

        payload = {
            "acquirer_reconciliation": [],
            "additional_info": {
                "authentication_code": None,
                "available_balance": None,
                "ip_address": "186.12.187.240",
                "items": [
                    {
                        "category_id": category.title,
                        "description": product.description,
                        "id": str(product.id),
                        "picture_url": None,
                        "quantity": "5",
                        "title": product.title,
                        "unit_price": product.price,
                    }
                ],
                "nsu_processadora": None,
            },
            "authorization_code": None,
            "binary_mode": True,
            "brand_id": None,
            "build_version": "2.129.1",
            "call_for_authorize_id": None,
            "captured": True,
            "card": {
                "cardholder": {
                    "identification": {"number": "11111111", "type": "DNI"},
                    "name": "APRO",
                },
                "date_created": "2023-01-30T07:40:20.000-04:00",
                "date_last_updated": "2023-01-30T07:40:20.000-04:00",
                "expiration_month": 11,
                "expiration_year": 2025,
                "first_six_digits": "503175",
                "id": None,
                "last_four_digits": "0604",
            },
            "charges_details": [],
            "collector_id": 643565524,
            "corporation_id": None,
            "counter_currency": None,
            "coupon_amount": 0,
            "currency_id": "ARS",
            "date_approved": "2023-01-30T07:40:21.007-04:00",
            "date_created": "2023-01-30T07:40:20.824-04:00",
            "date_last_updated": "2023-01-30T07:40:21.007-04:00",
            "date_of_expiration": "2023-02-02T08:38:13.000-04:00",
            "deduction_schema": None,
            "description": "Test title",
            "differential_pricing_id": None,
            "external_reference": None,
            "fee_details": [
                {"amount": 2.26, "fee_payer": "collector", "type": "mercadopago_fee"}
            ],
            "financing_group": None,
            "id": 1311430300,
            "installments": 1,
            "integrator_id": None,
            "issuer_id": "3",
            "live_mode": False,
            "marketplace_owner": 643565524,
            "merchant_account_id": None,
            "merchant_number": None,
            "metadata": {},
            "money_release_date": "2023-02-17T07:40:21.007-04:00",
            "money_release_schema": None,
            "money_release_status": None,
            "notification_url": "https://52ad-2803-9800-988a-930d-30fc-24a3-aa0b-d7e0.sa.ngrok.io/api/checkout/notify/mp/",
            "operation_type": "regular_payment",
            "order": {"id": "7493675291", "type": "mercadopago"},
            "payer": {
                "first_name": None,
                "last_name": None,
                "email": user.email,
                "identification": {"number": str(user.id), "type": "DNI"},
                "phone": {"area_code": None, "number": None, "extension": None},
                "type": None,
                "entity_type": None,
                "id": "429679419",
            },
            "payment_method": {"id": "master", "type": "credit_card"},
            "payment_method_id": "master",
            "payment_type_id": "credit_card",
            "platform_id": None,
            "point_of_interaction": {
                "business_info": {"sub_unit": "checkout_pro", "unit": "online_payments"},
                "type": "UNSPECIFIED",
            },
            "pos_id": None,
            "processing_mode": "aggregator",
            "refunds": [],
            "shipping_amount": 0,
            "sponsor_id": None,
            "statement_descriptor": "LACANDELA",
            "status": "approved",
            "status_detail": "accredited",
            "store_id": None,
            "taxes_amount": 0,
            "transaction_amount": 55,
            "transaction_amount_refunded": 0,
            "transaction_details": {
                "acquirer_reference": None,
                "external_resource_url": None,
                "financial_institution": None,
                "installment_amount": 55,
                "net_received_amount": 52.74,
                "overpaid_amount": 0,
                "payable_deferral_period": None,
                "payment_method_reference_id": None,
                "total_paid_amount": 55,
            },
        }

        order = self.service.create_order(payload)

        order_products = order.get_order_products()

        self.assertTrue(order)

        self.assertEqual(order.buyer, user)

        self.assertEqual(order_products[0].product, product)

    # TODO: Test invalid data reject in create order
