from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from apps.cart.meta import get_app_model, get_secondary_model

from db.models import Category, Product

MY_CART_URL = reverse("api:my-cart")  # cart API url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_cart_item_detail_url(cart_item):
    """
    Gets the cart item detail url of entered item
    """
    return reverse("api:cart_item", kwargs={"pk": cart_item.id})


class PublicCartApiTests(TestCase):
    """
    Tests Cart Api from public api
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        self.user = get_user_model().objects.create(email="testuser@test.com")

        self.cart = self.model.objects.create(user=self.user)

        self.category = Category.objects.create(title="TestCategory")

        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

    def test_cart_view_public_user_reject(self):
        """
        Tests if public user can't access to cart api view
        """
        res = self.client.get(MY_CART_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cart_view_post_public_user_reject(self):
        """
        Tests if public user can't post product in cart api view
        """

        payload = {
            "product": self.product.id,  # cart payload
            "count": 5,
        }

        res = self.client.post(MY_CART_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cart_view_delete_public_user_reject(self):
        """
        Tests if public user can't delete product in cart api view
        """

        mock_cart_item = {
            "cart": self.cart,  # cart payload
            "product": self.product,
            "count": 5,
        }
        cart_item = get_secondary_model().objects.create(**mock_cart_item)

        cart_item_url = get_cart_item_detail_url(cart_item)

        res = self.client.delete(cart_item_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserCartApiTests(TestCase):
    """
    Tests Cart Api from public api
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        # User Authenticate

        main_user_data = {"email": "testuser@test.com", "password": "Test123"}
        self.main_user = get_user_model().objects.create_user(
            **main_user_data  # create user
        )

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        # Product creation

        self.category = Category.objects.create(title="TestCategory")

        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

        # Cart creation

        self.cart = self.model.objects.create(user=self.main_user, total_items=5)

        self.cart_item = get_secondary_model().objects.create(
            product=self.product, cart=self.cart, count=5
        )

    def test_cart_view_normal_user_successful(self):
        """
        Tests if normal user can access to cart api view and see his cart
        """
        res = self.client.get(
            MY_CART_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.cart.id)
        self.assertContains(res, self.cart_item.product.title)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_auto_create_cart_view_normal_user_successful(self):
        """
        Tests if normal user without current cart can see cart api
        """
        new_user_data = {"email": "testnocartuser@test.com", "password": "Test123"}
        user = get_user_model().objects.create_user(**new_user_data)  # create user

        res_token = self.client.post(TOKEN_URL, new_user_data)  # get user token
        user_token = res_token.data["token"]

        res = self.client.get(MY_CART_URL, HTTP_AUTHORIZATION=f"Bearer {user_token}")

        self.assertContains(res, user.id)
        self.assertTrue(res.data["data"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cart_view_post_cart_item_normal_user_successful(self):
        """
        Tests if normal user can post an item in cart
        """

        payload = {
            "product": self.product.id,  # cart payload
            "count": 5,
        }

        res_post = self.client.post(MY_CART_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res_post.data["data"]["product"]["id"], self.product.id)
        self.assertEqual(res_post.data["data"]["product"]["title"], self.product.title)
        self.assertEqual(res_post.data["data"]["count"], 5 + payload["count"])

        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)

        res_get = self.client.get(MY_CART_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertTrue(res_get.data["data"]["items"])
        self.assertEqual(len(res_get.data["data"]["items"]), 1)

        self.assertEqual(res_get.data["data"]["items"][0]["product"]["id"], self.product.id)
        self.assertEqual(res_get.data["data"]["total_items"], 5 + payload["count"])
        self.assertEqual(res_get.data["data"]["items"][0]["count"], 5 + payload["count"])

    def test_auto_cart_view_post_cart_item_normal_user_successful(self):
        """
        Tests if normal user without current cart can post an item in cart
        """
        new_user_data = {"email": "testnocartuser@test.com", "password": "Test123"}
        get_user_model().objects.create_user(**new_user_data)  # create user

        res_token = self.client.post(TOKEN_URL, new_user_data)  # get user token
        user_token = res_token.data["token"]

        payload = {
            "product": self.product.id,  # cart payload
            "count": 5,
        }

        res_post = self.client.post(MY_CART_URL, payload, HTTP_AUTHORIZATION=f"Bearer {user_token}")

        self.assertEqual(res_post.data["data"]["product"]["id"], self.product.id)
        self.assertEqual(res_post.data["data"]["product"]["title"], self.product.title)
        self.assertEqual(res_post.data["data"]["count"], payload["count"])

        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)

        res_get = self.client.get(MY_CART_URL, HTTP_AUTHORIZATION=f"Bearer {user_token}")

        self.assertTrue(res_get.data["data"]["items"])
        self.assertEqual(len(res_get.data["data"]["items"]), 1)

        self.assertEqual(res_get.data["data"]["items"][0]["product"]["id"], self.product.id)
        self.assertEqual(res_get.data["data"]["total_items"], payload["count"])
        self.assertEqual(res_get.data["data"]["items"][0]["count"], payload["count"])

    def test_cart_view_post_cart_item_insufficient_stock_normal_user_reject(self):
        """
        Tests if normal user can't post an item in cart with insufficient stock
        """
        # updating stock
        self.product.stock = 4
        self.product.save()

        payload = {
            "product": self.product.id,  # cart payload
            "count": 5,
        }

        res_post = self.client.post(MY_CART_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res_post.status_code, status.HTTP_400_BAD_REQUEST)

        res_get = self.client.get(MY_CART_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(len(res_get.data["data"]["items"]), 0)

    def test_cart_view_delete_cart_item_normal_user_successful(self):
        """
        Tests if normal user can delete product in cart api view
        """

        cart_item_url = get_cart_item_detail_url(self.cart_item)

        res_delete = self.client.delete(cart_item_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(get_secondary_model().DoesNotExist):
            get_secondary_model().objects.get(pk=self.cart_item.pk)

        res_get = self.client.get(MY_CART_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertFalse(res_get.data["data"]["items"])
        self.assertEqual(res_get.data["data"]["total_items"], 0)

    def test_cart_view_delete_no_existing_cart_item_normal_user_reject(self):
        """
        Tests if normal user can't delete not added product in cart api view
        """

        cart_item_url = MY_CART_URL + "412/"

        res_delete = self.client.delete(cart_item_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_cart_view_delete_cart_item_of_other_user_reject(self):
        """
        Tests if normal user can't delete product of other user in cart api view
        """
        # Another user create
        new_user_data = {"email": "testnocartuser@test.com", "password": "Test123"}
        new_user = get_user_model().objects.create_user(**new_user_data)  # create user

        user_cart = self.model.objects.create(user=new_user)
        cart_item = user_cart.add_product(self.product, 5)

        cart_item_url = get_cart_item_detail_url(cart_item)

        res_delete = self.client.delete(
            cart_item_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",  # current user token
        )

        self.assertEqual(res_delete.status_code, status.HTTP_401_UNAUTHORIZED)
