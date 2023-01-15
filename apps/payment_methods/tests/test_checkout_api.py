from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from db.models import Cart

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_checkout_of(method: str, cart_id: int) -> str:
    """
    Gets checkout url of entered payment method

    Args:
        method(str): name of entered method
        cart_id(int) : id of selected cart

    Returns:
        Checkout url of entered method
    """
    return reverse("api:checkout", kwargs={"method": method, "cart_id": cart_id})


class PublicCheckoutApiTests(TestCase):
    """
    Tests checkout api with public user
    """

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create(email="testemail@test.com")

        self.cart = Cart.objects.create(user=self.user)

    def test_checkout_view_mp_method_public_user_reject(self):
        """
        Tests if public user can't see checkout view
        """
        checkout_url = get_checkout_of("mp", self.cart.id)

        res = self.client.get(checkout_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCheckoutApiTests(TestCase):
    """
    Tests checkout api with authenticated user
    """

    def setUp(self):
        self.client = APIClient()

        self.user_data = {
            "email": "testemail@test.com",
            "password": "pass123"
        }
        self.user = get_user_model().objects.create(**self.user_data)

        res_token = self.client.post(TOKEN_URL, self.user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.cart = Cart.objects.create(user=self.user)

    def test_checkout_view_mp_method_public_user_reject(self):
        """
        Tests if public user can't see checkout view
        """
        checkout_url = get_checkout_of("mp", self.cart.id)

        res = self.client.get(checkout_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
