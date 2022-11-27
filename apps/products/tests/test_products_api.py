from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from db.models import Product, Category


PRODUCTS_LIST_URL = reverse("products:product-list")  # products list api url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_products_detail_url(products_list):
    """
    Gets the product detail url of the first product in list
    """
    return reverse("products:product-detail", kwargs={"pk": products_list[0].id})


class PublicProductsAPITests(TestCase):
    """
    Tests products api with public client
    """

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(title="TestCategory")

        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "selled": 11,
        }

        self.product = Product.objects.create(**self.mock_product)

    def test_products_list_get_public_successful(self):
        """
        Tests if public user can see the products list
        """

        res = self.client.get(PRODUCTS_LIST_URL)

        self.assertContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_list_post_public_reject(self):
        """
        Tests if public user can't post into products list
        """
        payload = {
            "title": "Test title 2",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category.id,
            "selled": 11,
        }

        res = self.client.post(PRODUCTS_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_products_detail_get_public_successful(self):
        """
        Tests if public user can see the detail of a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertContains(res, products_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_update_public_reject(self):
        """
        Tests if public user can't update a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",  # Mock update product
            "description": "New Test description",
        }

        res = self.client.patch(product_url, payload)

        self.product.refresh_from_db()

        self.assertEqual(self.product.title, self.mock_product["title"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_products_detail_delete_public_reject(self):
        """
        Tests if public user can't delete a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.delete(product_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserProductsAPITests(TestCase):
    """
    Tests products api with private normal user
    """

    def setUp(self):
        self.client = APIClient()

        # Create Product

        self.category = Category.objects.create(title="TestCategory")

        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "selled": 11,
        }

        self.product = Product.objects.create(**self.mock_product)

        # User authenticate

        user_data = {"email": "testuser@test.com", "password": "testPassword"}

        self.user = get_user_model().objects.create_user(**user_data)
        self.client.force_authenticate(user=self.user)

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

    def test_products_list_get_normal_user_successful(self):
        """
        Tests if normal user can see the products list
        """

        res = self.client.get(PRODUCTS_LIST_URL)

        self.assertContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_list_post_normal_user_reject(self):
        """
        Tests if normal user can't post into products list
        """
        payload = {
            "title": "Test title 2",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category.id,
            "selled": 11,
        }

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_products_detail_get_normal_user_successful(self):
        """
        Tests if normal user can see the detail of a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertContains(res, products_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_update_normal_user_reject(self):
        """
        Tests if normal user can't update a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",  # Mock update product
            "description": "New Test description",
        }

        res = self.client.patch(
            product_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.title, self.mock_product["title"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_products_detail_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.delete(
            product_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperuserProductsAPITests(TestCase):
    """
    Tests products api with private superuser
    """

    def setUp(self):
        self.client = APIClient()

        # Create Product

        self.category = Category.objects.create(title="TestCategory")

        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "selled": 11,
        }

        self.product = Product.objects.create(**self.mock_product)

        # User authenticate

        user_data = {"email": "testuser@test.com", "password": "testPassword"}

        self.superuser = get_user_model().objects.create_superuser(**user_data)
        self.client.force_authenticate(user=self.superuser)

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

    def test_products_list_get_superuser_successful(self):
        """
        Tests if superuser can see the products list
        """

        res = self.client.get(PRODUCTS_LIST_URL)

        self.assertContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_list_post_superuser_successful(self):
        """
        Tests if superuser can post into products list
        """
        payload = {
            "title": "Test title 2",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category.id,
            "selled": 11,
        }

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_products_list_post_existing_product_superuser_reject(self):
        """
        Tests if superuser can't create an existing product
        """
        mock_product = {
            "title": "Test title 2",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "selled": 11,
        }

        Product.objects.create(**mock_product)

        payload = {**mock_product, "category": self.category.id}

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_products_detail_get_superuser_successful(self):
        """
        Tests if superuser can see the detail of a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertContains(res, products_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_update_superuser_successful(self):
        """
        Tests if superuser can update a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",  # Mock update product
            "description": "New Test description",
        }

        res = self.client.patch(
            product_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.product.refresh_from_db()

        self.assertEqual(self.product.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_delete_superuser_successful(self):
        """
        Tests if superuser can delete a product
        """
        products_list = Product.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.delete(
            product_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
