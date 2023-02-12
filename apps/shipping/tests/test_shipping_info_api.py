from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from apps.shipping.meta import get_app_model

SHIPPING_INFO_URL = reverse("api:shipping_info")


def get_shipping_info_url(shipping_instance: get_app_model()):
    """
    Gets shipping info entered instance url

    Args:
        shipping_instance: instance from which the url is obtained

    Returns:
        obtained url
    """
    return reverse("api:shipping_info", kwargs={"id": shipping_instance.id})


class PublicShippingInfoAPITests(TestCase):
    """
    Tests Shipping Info Api with public client
    """

    def setUp(self):
        self.client = APIClient()
        self.model = get_app_model()

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = self.model(**self.mock_shipping_info)

    def test_ship_info_list_view_public_user_get_reject(self):
        """
        Tests if public user can't list shipping info api
        """
        res = self.client.get(SHIPPING_INFO_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_get_reject(self):
        """
        Tests if public user can't retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.get(retrieve_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_list_view_public_user_post_reject(self):
        """
        Tests if public user can't post in list shipping info api
        """
        payload = self.mock_shipping_info = {
            "user": self.user.id,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

        res = self.client.post(SHIPPING_INFO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_put_reject(self):
        """
        Tests if public user can't put retrieve shipping info api
        """

    def test_ship_info_retrieve_view_public_user_patch_reject(self):
        """
        Tests if public user can't patch retrieve shipping info api
        """

    def test_ship_info_retrieve_view_public_user_delete_reject(self):
        """
        Tests if public user can't delete retrieve shipping info api
        """
