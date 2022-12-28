from random import randint

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.products.meta import get_app_model
from db.models import Category


def get_related_products_url(productId: int, filter: str = None, value: str = None):
    """
    Gets the related products url from entered 'productId'
    """
    path = reverse("api:product-get-related-products", kwargs={"pk": productId})

    if filter and value:
        path += f"?{filter}={value}"

    return path


def create_products(quantity: int, category: Category):
    """
    Create a list of products with passed quantity
    """
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
        "category": category,
        "sold": 11,
    }

    product_list = []

    for pd in range(1, quantity + 1):
        mock_product["title"] = f"Test title {pd * randint(1000,10000)}"
        product = get_app_model().objects.create(**mock_product)
        product.save()

        product_list.append(product)

    return product_list


class PublicRelatedProductsTests(TestCase):
    """
    Tests public client in Related Products API
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        self.parent_category = Category.objects.create(
            title="Test Parent Category",
        )
        self.parent_category.save()

        self.child_category = Category.objects.create(
            title="Test Child Category", parent=self.parent_category
        )
        self.child_category.save()

        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.child_category,
            "sold": 11,
        }

        self.product = self.model.objects.create(**self.mock_product)
        self.product.save()

    def test_related_products_list_get_successful(self):
        """
        Tests if public user can list related products api
        """
        mock_product = self.mock_product
        mock_product["title"] = "Related Product"

        related_product = self.model.objects.create(
            **mock_product  # create related product
        )

        new_category = Category.objects.create(
            parent=self.parent_category, title="Test Child Category 2"
        )
        mock_product = self.mock_product
        mock_product["title"] = "No Related Product"
        mock_product["category"] = new_category

        no_related_product = self.model.objects.create(
            **mock_product  # create no related product
        )

        related_list_url = get_related_products_url(self.product.id)

        res = self.client.get(related_list_url)

        self.assertNotContains(res, self.product)
        self.assertContains(res, related_product)
        self.assertNotContains(res, no_related_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_related_products_list_get_bad_pk_reject(self):
        """
        Tests if public user can list related products api
        """
        mock_product = self.mock_product
        mock_product["title"] = "Related Product"

        self.model.objects.create(**mock_product)  # create related product

        related_list_url = get_related_products_url("BadPk")

        res = self.client.get(related_list_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_products_list_post_not_allowed_successful(self):
        """
        Tests if public user can't post in related products api
        """
        mock_product = self.mock_product
        mock_product["title"] = "Related Product"

        self.model.objects.create(**mock_product)  # create related product

        payload = {**self.mock_product}
        payload["title"] = "Related Product 2"

        related_list_url = get_related_products_url(self.product.id)

        res = self.client.post(related_list_url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_related_products_list_auto_limit_results_ten_successful(self):
        """
        Tests if Related products has auto limit result in ten
        """

        create_products(15, self.child_category)  # create 15 products

        related_products_url = get_related_products_url(self.product.id)

        res = self.client.get(related_products_url)

        self.assertEqual(len(res.data), 10)

        self.assertNotContains(res, self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_related_products_list_limit_results_successful(self):
        """
        Tests if Related products has limit result
        """

        create_products(15, self.child_category)  # create 15 products

        related_products_url = get_related_products_url(
            self.product.id,
            "limit",
            "5",
        )

        res = self.client.get(related_products_url)

        self.assertEqual(len(res.data), 5)

        self.assertNotContains(res, self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
