from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from db.models import Order, Category, Product, ShippingInfo

ORDER_LIST_URL = reverse("api:order-list")  # order list url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


class PublicOrdersAPITests(TestCase):
    """
    Tests orders by public client
    """

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com"  # create user for order
        )

        category = Category.objects.create(
            title="TestCategory"  # create category for product
        )
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(
            **self.mock_product  # create product for order
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(
            **self.mock_shipping_info  # create shipping info for order
        )

        self.mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        self.order = Order.objects.create(**self.mock_order)

    def test_order_list_get_public_reject(self):
        """
        Tests if public user can't see order list
        """
        res = self.client.get(ORDER_LIST_URL)

        self.assertNotContains(res, self.order)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
