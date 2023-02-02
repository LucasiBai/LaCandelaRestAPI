from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from db.models import Category, Product, ShippingInfo

CHECKOUT_NOTIFICATION_URLS = {"mp": reverse("api:checkout_notify", kwargs={"method": "mP"})}


class PublicCheckoutNotificationApiTests(TestCase):
    """
    Tests Checkout Notification Api with public user
    """

    def setUp(self):
        self.client = APIClient()

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

    def test_checkout_notification_mp_post_format_successful(self):
        """
        Tests if public user can post in checkout notification Api
        """
        payload = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "date_created": "2015-03-25T10:04:58.396-04:00",
            "application_id": 123123123,
            "user_id": 44444,
            "version": 1,
            "api_version": "v1",
            "action": "payment.created",
            "data": {
                "id": 1311430300
            }
        }

        res = self.client.post(CHECKOUT_NOTIFICATION_URLS["mp"], payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_checkout_notification_mp_post_valid_payment_successful(self):
        """
        Tests if public user can post in checkout notification Api
        and client creates an order if payment was validated
        """
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

        res = self.client.post(CHECKOUT_NOTIFICATION_URLS["mp"], payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue(res.data)

        self.assertEqual(res.data["user"]["email"], "test_user_80507629@testuser.com")

        # TODO : search order

    # TODO : Test rejected payment
    def test_checkout_notification_unexpected_method_reject(self):
        """
        Tests if public user can't post with unexpected method
        """
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

        url = reverse("api:checkout_notify", kwargs={"method": "invalid-method"})

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
