from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.products.meta import get_app_model
from db.models import Category


def get_related_products_url(productId: int):
    """
    Gets the related products url from entered 'productId'
    """
    return reverse("api:product-get-related-products", kwargs={"pk": productId})


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

        self.child_category = Category.objects.create(
            title="Test Child Category", parent=self.parent_category
        )

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
