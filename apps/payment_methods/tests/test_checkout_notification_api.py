from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CHECKOUT_NOTIFICATION_URL = reverse("api:checkout_notify")


class PublicCheckoutNotificationApiTests(TestCase):
    """
    Tests Checkout Notification Api with public user
    """

    def setUp(self):
        self.client = APIClient()

    def test_checkout_notification_post_successful(self):
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

        res = self.client.post(CHECKOUT_NOTIFICATION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
