from random import randint

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from db.models import Cart, Category, Product

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
        self.user = get_user_model().objects.create_user(**self.user_data)

        res_token = self.client.post(TOKEN_URL, self.user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.cart = Cart.objects.create(user=self.user)

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

        self.cart_item = self.cart.add_product(self.product, 5)

    def test_checkout_view_mp_method_normal_user_successful(self):
        """
        Tests if normal user can see own checkout view
        """
        checkout_url = get_checkout_of("mp", self.cart.id)

        res = self.client.get(checkout_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertContains(res, "user")
        self.assertContains(res, "preference")

        self.assertEqual(res.data["preference"]["payer"]["identification"]["number"], str(self.user.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_checkout_view_mp_method_normal_user_no_existing_cart_reject(self):
        """
        Tests if api rejects a no existing cart id
        """
        checkout_url = get_checkout_of("mp", randint(13212, 132214))

        res = self.client.get(checkout_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.data["message"], "cart id is invalid.")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_view_of_other_user_mp_method_normal_user_reject(self):
        """
        Tests if normal user can't see checkout view of other user
        """
        new_user = get_user_model().objects.create_user(email="newuser@test.com")

        user_cart = Cart.objects.create(user=new_user)

        checkout_url = get_checkout_of("mp", user_cart.id)

        res = self.client.get(checkout_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_view_normal_user_no_existing_method_reject(self):
        """
        Tests if api rejects a no existing method
        """
        checkout_url = get_checkout_of("no-existing-method", self.cart.id)

        res = self.client.get(checkout_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.data["message"], "method is invalid.")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Test remove cart items
