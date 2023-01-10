from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from apps.products.meta import get_app_model
from db.models import Category, Comment

PRODUCTS_LIST_URL = reverse("api:product-list")  # products list api url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_products_detail_url(products_list):
    """
    Gets the product detail url of the first product in list
    """
    return reverse("api:product-detail", kwargs={"pk": products_list[0].id})


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return PRODUCTS_LIST_URL + f"?{filter_name}={value}"


class PublicProductsAPITests(TestCase):
    """
    Tests products api with public client
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()  # product model

        self.category = Category.objects.create(title="TestCategory")

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
            "category": self.category,
            "sold": 11,
        }

        self.product = self.model.objects.create(**self.mock_product)

    def test_products_list_get_public_successful(self):
        """
        Tests if public user can see the products list
        """

        res = self.client.get(PRODUCTS_LIST_URL)

        self.assertContains(res, self.product)

        self.assertContains(res, "results")
        self.assertEqual(res.data["results"], 1)

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
            "sold": 11,
        }

        res = self.client.post(PRODUCTS_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_products_detail_get_public_successful(self):
        """
        Tests if public user can see the detail of a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertContains(res, products_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_product_detail_has_automatic_rate_successful(self):
        """
        Tests if products has automatic rate
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertEqual(res.data["rate"], 5.00)

    def test_product_detail_has_comment_rate_successful(self):
        """
        Tests if product detail has the rate of user comment
        """
        user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testPassword"
        )

        mock_comment = {
            "user": user,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        self.product.create_comment(**mock_comment)

        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertEqual(res.data["rate"], mock_comment["rate"])

    def test_product_detail_has_comment_rate_avg_successful(self):
        """
        Tests if product detail has the rate average of users comments
        """
        user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testPassword"
        )

        first_mock_comment = {
            "user": user,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        second_mock_comment = {**first_mock_comment, "rate": 2.4}

        self.product.create_comment(**first_mock_comment)
        self.product.create_comment(**second_mock_comment)

        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertEqual(res.data["rate"], 3.35)

    def test_product_detail_category_title_successful(self):
        """
        Tests if product detail 'category' has category title
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertEqual(self.category.title, res.data["category"])

    def test_products_detail_partial_update_public_reject(self):
        """
        Tests if public user can't partial update a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",  # Mock update product
            "description": "New Test description",
        }

        res = self.client.patch(product_url, payload)

        self.product.refresh_from_db()

        self.assertEqual(self.product.title, self.mock_product["title"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_products_detail_update_public_reject(self):
        """
        Tests if public user can't update a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",
            "description": "New Test description",
            "price": 1111,
            "images": [
                "http://testimgurl.com/1",
                "http://testimgurl.com/2",  # Mock product update data
                "http://testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category.id,
            "sold": 11,
        }

        res = self.client.put(product_url, payload)
        self.product.refresh_from_db()

        self.assertEqual(self.product.title, self.mock_product["title"])
        self.assertEqual(self.product.description, self.mock_product["description"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_products_detail_delete_public_reject(self):
        """
        Tests if public user can't delete a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.delete(product_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_products_min_price_filter_successful(self):
        """
        Tests if api has a min price filter endpoint
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1120,
        }

        new_product = self.model.objects.create(**new_mock_product)

        min_price_filter_url = get_filter_url("min_price", "1115")

        res = self.client.get(min_price_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_min_price_filter_include_equals_successful(self):
        """
        Tests if api has a min price filter endpoint includes equals
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1115,
        }

        new_product = self.model.objects.create(**new_mock_product)

        min_price_filter_url = get_filter_url("min_price", "1115")

        res = self.client.get(min_price_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_max_price_filter_successful(self):
        """
        Tests if api has a max price filter endpoint
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1120,
        }

        new_product = self.model.objects.create(**new_mock_product)

        max_price_filter_url = get_filter_url("max_price", "1115")

        res = self.client.get(max_price_filter_url)

        self.assertContains(res, self.product)
        self.assertNotContains(res, new_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_max_price_filter_include_equals_successful(self):
        """
        Tests if api has a max price filter endpoint includes equals
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1120,
        }

        new_product = self.model.objects.create(**new_mock_product)

        max_price_filter_url = get_filter_url("max_price", "1111")

        res = self.client.get(max_price_filter_url)

        self.assertContains(res, self.product)
        self.assertNotContains(res, new_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_title_filter_successful(self):
        """
        Tests if api has a title filter endpoint
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1112,
        }

        new_product = self.model.objects.create(**new_mock_product)

        title_filter_url = get_filter_url("title", "New")

        res = self.client.get(title_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_title_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a title filter endpoint no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1112,
        }

        new_product = self.model.objects.create(**new_mock_product)

        title_filter_url = get_filter_url("title", "new")

        res = self.client.get(title_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_category_filter_successful(self):
        """
        Tests if api has a category filter endpoint
        """
        category = Category.objects.create(
            title="New Test Category"  # create new category
        )

        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "category": category,
        }

        new_product = self.model.objects.create(**new_mock_product)

        category_filter_url = get_filter_url("category", category.title)

        res = self.client.get(category_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_category_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a category filter endpoint no case sensitive
        """
        category = Category.objects.create(
            title="New Test Category"  # create new category
        )

        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "category": category,
        }

        new_product = self.model.objects.create(**new_mock_product)

        category_filter_url = get_filter_url("category", category.title.lower())

        res = self.client.get(category_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_offset_filter_successful(self):
        """
        Tests if products starts with offset param
        """
        first_new_mock_product = {
            **self.mock_product,
            "title": "Test First New Product",
            "price": 1112,
        }
        first_new_product = self.model.objects.create(**first_new_mock_product)

        second_new_mock_product = {
            **self.mock_product,
            "title": "Test Second New Product",
            "price": 1112,
        }
        second_new_product = self.model.objects.create(**second_new_mock_product)

        offset_filter_url = get_filter_url("offset", "2")

        res = self.client.get(offset_filter_url)

        self.assertContains(res, first_new_product)
        self.assertContains(res, second_new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_limit_filter_successful(self):
        """
        Tests if products starts with offset param
        """
        first_new_mock_product = {
            **self.mock_product,
            "title": "Test First New Product",
            "price": 1112,
        }
        first_new_product = self.model.objects.create(**first_new_mock_product)

        second_new_mock_product = {
            **self.mock_product,
            "title": "Test Second New Product",
            "price": 1112,
        }
        second_new_product = self.model.objects.create(**second_new_mock_product)

        offset_filter_url = get_filter_url("limit", "2")

        res = self.client.get(offset_filter_url)

        self.assertContains(res, self.product)
        self.assertContains(res, first_new_product)
        self.assertNotContains(res, second_new_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_min_rate_filter_successful(self):
        """
        Tests if api has a min rate filter endpoint
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",  # creating new product
        }
        new_product = self.model.objects.create(**new_mock_product)

        user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testPassword",  # new user to create comment
        )

        mock_comment = {
            "user": user,
            "subject": "Test comment subject",  # new comment
            "content": "Test comment content",
            "rate": 4.3,
        }
        self.product.create_comment(**mock_comment)

        min_rate_filter_url = get_filter_url("min_rate", "5")

        res = self.client.get(min_rate_filter_url)

        self.assertContains(res, new_product)
        self.assertNotContains(res, self.product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_max_rate_filter_successful(self):
        """
        Tests if api has a max rate filter endpoint
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",  # creating new product
        }
        new_product = self.model.objects.create(**new_mock_product)

        user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testPassword",  # new user to create comment
        )

        mock_comment = {
            "user": user,
            "subject": "Test comment subject",  # new comment
            "content": "Test comment content",
            "rate": 4.3,
        }
        self.product.create_comment(**mock_comment)

        max_rate_filter_url = get_filter_url("max_rate", "4.3")

        res = self.client.get(max_rate_filter_url)

        self.assertContains(res, self.product)
        self.assertNotContains(res, new_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_price_asc_order_filter_successful(self):
        """
        Tests if api has a price ascendent order filter
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1000,
        }

        new_product = self.model.objects.create(**new_mock_product)

        price_asc_filter_url = get_filter_url("price_order", "asc")

        res = self.client.get(price_asc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_price_asc_order_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a price ascendent order filter no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1000,
        }

        new_product = self.model.objects.create(**new_mock_product)

        price_asc_filter_url = get_filter_url("price_order", "aSc")

        res = self.client.get(price_asc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_price_desc_order_filter_successful(self):
        """
        Tests if api has a price descendent order filter
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1500,
        }

        new_product = self.model.objects.create(**new_mock_product)

        price_desc_filter_url = get_filter_url("price_order", "desc")

        res = self.client.get(price_desc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_price_desc_order_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a price descendent order filter no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test New Product",
            "price": 1500,
        }

        new_product = self.model.objects.create(**new_mock_product)

        price_desc_filter_url = get_filter_url("price_order", "dEsC")

        res = self.client.get(price_desc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_title_asc_order_filter_successful(self):
        """
        Tests if api has a title ascendent order filter
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Second Product",
            "price": 1500,
        }

        new_product = self.model.objects.create(**new_mock_product)

        title_asc_filter_url = get_filter_url("title_order", "asc")

        res = self.client.get(title_asc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_title_asc_order_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a title ascendent order filter no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Second Product",
            "price": 1500,
        }

        new_product = self.model.objects.create(**new_mock_product)

        title_asc_filter_url = get_filter_url("title_order", "aSc")

        res = self.client.get(title_asc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_title_desc_order_filter_successful(self):
        """
        Tests if api has a title descendent order filter
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test U Product",
            "price": 1500,
        }

        new_product = self.model.objects.create(**new_mock_product)

        title_desc_filter_url = get_filter_url("title_order", "desc")

        res = self.client.get(title_desc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_title_desc_order_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a title descendent order filter no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test U Product",
            "price": 1500,
        }

        new_product = self.model.objects.create(**new_mock_product)

        title_desc_filter_url = get_filter_url("title_order", "DeSc")

        res = self.client.get(title_desc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_search_filter_by_title_successful(self):
        """
        Tests if api has a search filter thats search by title
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Search Title 1",
        }
        new_first_product = self.model.objects.create(**new_mock_product)

        new_mock_product["title"] = "Test Search Title 2"
        new_second_product = self.model.objects.create(**new_mock_product)

        search_filter_url = get_filter_url("search", "test search title")

        res = self.client.get(search_filter_url)

        self.assertNotContains(res, self.product)
        self.assertContains(res, new_first_product)
        self.assertContains(res, new_second_product)

    def test_products_search_filter_by_description_successful(self):
        """
        Tests if api has a search filter thats search by description
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Search Title 1",
            "description": "Test Search Description",
        }
        new_first_product = self.model.objects.create(**new_mock_product)

        new_mock_product["title"] = "Test Search Title 2"
        new_second_product = self.model.objects.create(**new_mock_product)

        search_filter_url = get_filter_url("search", "test search description")

        res = self.client.get(search_filter_url)

        self.assertNotContains(res, self.product)
        self.assertContains(res, new_first_product)
        self.assertContains(res, new_second_product)

    def test_products_search_filter_by_category_successful(self):
        """
        Tests if api has a search filter thats search by category
        """
        category = Category.objects.create(title="Test Second Category")

        new_mock_product = {
            **self.mock_product,
            "title": "Test Search Title 1",
            "category": category,
        }
        new_first_product = self.model.objects.create(**new_mock_product)

        new_mock_product["title"] = "Test Search Title 2"
        new_second_product = self.model.objects.create(**new_mock_product)

        search_filter_url = get_filter_url("search", "test second catego")

        res = self.client.get(search_filter_url)

        self.assertNotContains(res, self.product)
        self.assertContains(res, new_first_product)
        self.assertContains(res, new_second_product)

    def test_products_search_filter_with_limit_results_successful(self):
        """
        Tests if api search filter with limit filter, the 'results' are correct
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Search Title 1",
        }
        new_first_product = self.model.objects.create(**new_mock_product)

        new_mock_product["title"] = "Test Search Title 2"
        new_second_product = self.model.objects.create(**new_mock_product)

        search_filter_url = get_filter_url("search", "test search title") + "&limit=1"

        res = self.client.get(search_filter_url)

        self.assertNotContains(res, self.product)
        self.assertContains(res, new_first_product)
        self.assertNotContains(res, new_second_product)

        self.assertEqual(res.data["results"], 2)

    def test_products_search_filter_with_offset_results_successful(self):
        """
        Tests if api search filter with offset filter, the 'results' are correct
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Search Title 1",
        }
        new_first_product = self.model.objects.create(**new_mock_product)

        new_mock_product["title"] = "Test Search Title 2"
        new_second_product = self.model.objects.create(**new_mock_product)

        search_filter_url = get_filter_url("search", "test search title") + "&offset=2"

        res = self.client.get(search_filter_url)

        self.assertNotContains(res, self.product)
        self.assertNotContains(res, new_first_product)
        self.assertContains(res, new_second_product)

        self.assertEqual(res.data["results"], 2)

    def test_products_sold_asc_order_filter_successful(self):
        """
        Tests if api has a sold ascendent order filter
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Second Product",
            "sold": 10,
        }

        new_product = self.model.objects.create(**new_mock_product)

        sold_asc_filter_url = get_filter_url("sold_order", "asc")

        res = self.client.get(sold_asc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_sold_asc_order_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a sold ascendent order filter no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Second Product",
            "sold": 10,
        }

        new_product = self.model.objects.create(**new_mock_product)

        sold_asc_filter_url = get_filter_url("sold_order", "aSc")

        res = self.client.get(sold_asc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_sold_desc_order_filter_successful(self):
        """
        Tests if api has a sold descendent order filter
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Second Product",
            "sold": 15,
        }

        new_product = self.model.objects.create(**new_mock_product)

        sold_desc_filter_url = get_filter_url("sold_order", "desc")

        res = self.client.get(sold_desc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_sold_desc_order_filter_no_case_sensitive_successful(self):
        """
        Tests if api has a sold descendent order filter no case sensitive
        """
        new_mock_product = {
            **self.mock_product,
            "title": "Test Second Product",
            "sold": 15,
        }

        new_product = self.model.objects.create(**new_mock_product)

        sold_desc_filter_url = get_filter_url("sold_order", "dEsC")

        res = self.client.get(sold_desc_filter_url)

        self.assertEqual(res.data["data"][0]["id"], new_product.id)
        self.assertEqual(res.data["data"][1]["id"], self.product.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateUserProductsAPITests(TestCase):
    """
    Tests products api with private normal user
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()  # product model

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
            "sold": 11,
        }

        self.product = self.model.objects.create(**self.mock_product)

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
            "sold": 11,
        }

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_products_detail_get_normal_user_successful(self):
        """
        Tests if normal user can see the detail of a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertContains(res, products_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_partial_update_normal_user_reject(self):
        """
        Tests if normal user can't partial update a product
        """
        products_list = self.model.objects.all()
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

    def test_products_detail_update_normal_user_reject(self):
        """
        Tests if normal user can't update a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",
            "description": "New Test description",
            "price": 1111,
            "images": [
                "http://testimgurl.com/1",
                "http://testimgurl.com/2",  # Mock product update data
                "http://testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category.id,
            "sold": 11,
        }

        res = self.client.put(
            product_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.product.refresh_from_db()

        self.assertEqual(self.product.title, self.mock_product["title"])
        self.assertEqual(self.product.description, self.mock_product["description"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_products_detail_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete a product
        """
        products_list = self.model.objects.all()
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

        self.model = get_app_model()  # product model

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
            "sold": 11,
        }

        self.product = self.model.objects.create(**self.mock_product)

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
                "http://testimgurl.com/1",
                "http://testimgurl.com/2",  # Mock product data
                "http://testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category.id,
            "sold": 11,
        }

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.assertIn("rate", res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_products_list_post_invalid_urls_superuser_reject(self):
        """
        Tests if superuser can't post with invalid urls into products list
        """
        payload = {
            "title": "Test title 2",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testinvalidurl/1",
                "testinvalidurl/2",  # Mock product data
                "testinvalidurl/3",
            ],
            "stock": 11,
            "category": self.category.id,
            "sold": 11,
        }

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.assertIn("images", res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

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
            "sold": 11,
        }

        self.model.objects.create(**mock_product)

        payload = {**mock_product, "category": self.category.id}

        res = self.client.post(
            PRODUCTS_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_products_detail_get_superuser_successful(self):
        """
        Tests if superuser can see the detail of a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.get(product_url)

        self.assertContains(res, products_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_partial_update_superuser_successful(self):
        """
        Tests if superuser can partial update a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",  # Mock update product
            "description": "New Test description",
        }

        res = self.client.patch(
            product_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.product.refresh_from_db()

        self.assertEqual(res.data["title"], payload["title"])
        self.assertEqual(res.data["description"], payload["description"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_update_superuser_successful(self):
        """
        Tests if superuser can update a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        payload = {
            "title": "New Test Title",
            "description": "New Test description",
            "price": 1111,
            "images": [
                "http://testimgurl.com/1",
                "http://testimgurl.com/2",  # Mock product update data
                "http://testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category.id,
            "sold": 11,
        }

        res = self.client.put(
            product_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.product.refresh_from_db()

        self.assertEqual(self.product.title, payload["title"])
        self.assertEqual(self.product.description, payload["description"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_products_detail_delete_superuser_successful(self):
        """
        Tests if superuser can delete a product
        """
        products_list = self.model.objects.all()
        product_url = get_products_detail_url(products_list)

        res = self.client.delete(
            product_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
