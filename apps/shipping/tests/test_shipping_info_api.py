from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.shipping.meta import get_app_model

SHIPPING_INFO_URL = reverse("api:shipping_info")


class PublicShippingInfoAPITests(TestCase):
    """
    Tests Shipping Info Api with public client
    """

    def setUp(self):
        self.client = APIClient()
