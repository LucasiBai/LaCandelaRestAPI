from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CHECKOUT_NOTIFICATION_URLS = {"mp": reverse("api:checkout_notify", kwargs={"method": "mP"})}


class PublicCheckoutNotificationApiTests(TestCase):
    """
    Tests Checkout Notification Api with public user
    """

    def setUp(self):
        self.client = APIClient()

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
                "id": "999999999"
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
            'data': {'id': '1311430300'},
            'date_created': '2023-01-30T11:40:20Z',
            'id': 104791905287,
            'live_mode': False,
            'type': 'payment',
            'user_id': '643565524'
        }

        res = self.client.post(CHECKOUT_NOTIFICATION_URLS["mp"], payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # TODO: Test if api create order

    # TODO: Test unexpected method
