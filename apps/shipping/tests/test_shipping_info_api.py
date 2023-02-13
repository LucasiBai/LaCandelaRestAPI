from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from apps.shipping.meta import get_app_model

SHIPPING_INFO_URL = reverse("api:shipping_info")  # shipping info API url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


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
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = self.mock_shipping_info = {
            "user": self.user.id,
            "address": "Updated Test address",
            "receiver": "test receiver name",
            "receiver_dni": 87654321,
        }

        res = self.client.put(retrieve_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_patch_reject(self):
        """
        Tests if public user can't patch retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = self.mock_shipping_info = {
            "address": "Updated Test address",
            "receiver_dni": 87654321,
        }

        res = self.client.patch(retrieve_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_delete_reject(self):
        """
        Tests if public user can't delete retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.delete(retrieve_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserShippingInfoAPITests(TestCase):
    """
    Tests Shipping Info Api with private user
    """

    def setUp(self):
        self.client = APIClient()
        self.model = get_app_model()

        user_data = {
            "email": "testemail@test.com",
            "password": "testPassword123"
        }
        self.user = get_user_model().objects.create_user(
            **user_data, first_name="Test", last_name="Testi"
        )

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

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
        res = self.client.get(SHIPPING_INFO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ship_info_retrieve_view_public_user_get_reject(self):
        """
        Tests if public user can't retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

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

        res = self.client.post(SHIPPING_INFO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_ship_info_retrieve_view_public_user_put_reject(self):
        """
        Tests if public user can't put retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = self.mock_shipping_info = {
            "user": self.user.id,
            "address": "Updated Test address",
            "receiver": "test receiver name",
            "receiver_dni": 87654321,
        }

        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ship_info_retrieve_view_public_user_patch_reject(self):
        """
        Tests if public user can't patch retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = self.mock_shipping_info = {
            "address": "Updated Test address",
            "receiver_dni": 87654321,
        }

        res = self.client.patch(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ship_info_retrieve_view_public_user_delete_reject(self):
        """
        Tests if public user can't delete retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
