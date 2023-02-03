from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status

from apps.payment_methods.utils.order_creation import OrderCreation, MercadoPagoMethod
from db.models import ShippingInfo, Category, Product, Order


class OrderMercadoPagoMethodTests(TestCase):
    def setUp(self):
        self.order_creation_model = OrderCreation

        # User creation
        self.user = get_user_model().objects.create(email="test_user_80507629@testuser.com")

        mock_user_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        ShippingInfo.objects.create(**mock_user_shipping_info)

        # Product creation
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
        self.product = Product.objects.create(**mock_product)

    def test_auto_mercado_pago_order_creation_successful(self):
        """
        Tests if generated order creation auto generate MercadoPagoMethod
        """

        order_creation = self.order_creation_model()

        self.assertEquals(str(order_creation.get_order_method()), str(MercadoPagoMethod()))

    def test_mercado_pago_get_response_valid_order_successful(self):
        """
        Tests if order creation can create a response with Mercado Pago Method
        """
        order_creation = self.order_creation_model()  # creates order creation

        payload = {
            'action': 'payment.created',
            'api_version': 'v1',
            'data': {'id': 1311430300},
            'date_created': '2023-01-30T11:40:20Z',
            'id': 104791905287,
            'live_mode': False,
            'type': 'payment',
            'user_id': '643565524'
        }

        response = order_creation.get_response(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data)

        self.assertEqual(response.data["user"]["email"], "test_user_80507629@testuser.com")

        order = Order.objects.filter(buyer__email=response.data["user"]["email"]).last()

        order_product = order.get_order_products()[-1]

        self.assertEqual(order_product.product, self.product)

    # TODO: Create test of change_order_method
