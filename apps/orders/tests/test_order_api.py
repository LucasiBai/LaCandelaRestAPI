from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.meta import get_app_model
from db.models import Category, Product, ShippingInfo

ORDER_LIST_URL = reverse("api:order-list")  # order list url

MINE_URL = reverse("api:order-get-mine-orders")  # mine order list url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_order_detail_url(order_list):
    """
    Gets the order detail url of the first order in list
    """
    return reverse("api:order-detail", kwargs={"pk": order_list[0].id})


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return ORDER_LIST_URL + f"?{filter_name}={value}"


class PublicOrdersAPITests(TestCase):
    """
    Tests orders by public client
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()  # order model

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com"  # create user for order
        )

        category = Category.objects.create(
            title="TestCategory"  # create category for product
        )
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(
            **self.mock_product  # create product for order
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(
            **self.mock_shipping_info  # create shipping info for order
        )

        self.mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        self.order = self.model.objects.create(**self.mock_order)

    def test_order_list_get_public_reject(self):
        """
        Tests if public user can't see order list
        """
        res = self.client.get(ORDER_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_get_public_reject(self):
        """
        Tests if public user can't see order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        res = self.client.get(order_detail_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_list_post_public_reject(self):
        """
        Tests if public user can't post order list
        """
        payload = {
            "buyer": self.user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info.id,
        }

        res = self.client.post(ORDER_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_patch_public_reject(self):
        """
        Tests if public user can't patch order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        payload = {
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ]
        }

        res = self.client.patch(order_detail_url, payload)
        self.order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_put_public_reject(self):
        """
        Tests if public user can't put order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        payload = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ],
            "shipping_info": self.shipping_info,
        }

        res = self.client.put(order_detail_url, payload)
        self.order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_delete_public_reject(self):
        """
        Tests if public user can't delete order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        res = self.client.delete(order_detail_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersOrdersAPITests(TestCase):
    """
    Tests orders by private user
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()  # order model

        main_user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.main_user = get_user_model().objects.create_user(
            **main_user_data  # create main user
        )

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com"  # create user for order
        )

        category = Category.objects.create(
            title="TestCategory"  # create category for product
        )
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(
            **self.mock_product  # create product for order
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(
            **self.mock_shipping_info  # create shipping info for order
        )

        self.mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        self.order = self.model.objects.create(**self.mock_order)

    def test_order_list_get_normal_user_reject(self):
        """
        Tests if normal user can't see order list
        """
        res = self.client.get(
            ORDER_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_mine_list_normal_user_successful(self):
        """
        Tests if exists mine endpoint with current user orders
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        first_user_order = self.model.objects.create(**mock_order)
        second_user_order = self.model.objects.create(**mock_order)

        res = self.client.get(MINE_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertNotContains(res, self.order.id)
        self.assertContains(res, first_user_order.id)
        self.assertContains(res, second_user_order.id)

        self.assertIn("results", res.data)
        self.assertIn("data", res.data)

        self.assertEqual(res.data["results"], 2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_mine_list_normal_user_with_offset_filter_successful(self):
        """
        Tests if exists mine endpoint with current user orders
        with offset filter
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        first_user_order = self.model.objects.create(**mock_order)
        second_user_order = self.model.objects.create(**mock_order)
        third_user_order = self.model.objects.create(**mock_order)

        offset_filter_url = MINE_URL + "?offset=2"

        res = self.client.get(
            offset_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertNotContains(res, self.order.id)
        self.assertNotContains(res, first_user_order.id)
        self.assertContains(res, second_user_order.id)
        self.assertContains(res, third_user_order.id)

        self.assertIn("results", res.data)
        self.assertIn("data", res.data)

        self.assertEqual(res.data["results"], 3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_mine_list_normal_user_with_limit_filter_successful(self):
        """
        Tests if exists mine endpoint with current user orders
        with limit filter
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        first_user_order = self.model.objects.create(**mock_order)
        second_user_order = self.model.objects.create(**mock_order)
        third_user_order = self.model.objects.create(**mock_order)

        limit_filter_url = MINE_URL + "?limit=2"

        res = self.client.get(
            limit_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertNotContains(res, self.order.id)
        self.assertContains(res, first_user_order.id)
        self.assertContains(res, second_user_order.id)
        self.assertNotContains(res, third_user_order.id)

        self.assertIn("results", res.data)
        self.assertIn("data", res.data)

        self.assertEqual(res.data["results"], 3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_mine_list_normal_user_post_not_allowed_reject(self):
        """
        Tests if user can't post in mine list
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        payload = {
            "buyer": self.main_user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info.id,
        }
        res = self.client.post(
            MINE_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_order_detail_get_normal_user_reject(self):
        """
        Tests if normal user can't see order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        res = self.client.get(
            order_detail_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_order_list_post_normal_user_successful(self):
        """
        Tests if normal user can post order list
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        payload = {
            "buyer": self.main_user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info.id,
        }

        res = self.client.post(
            ORDER_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_order_list_post_normal_user_for_other_user_reject(self):
        """
        Tests if normal user can't post in order list for other user
        """

        payload = {
            "buyer": self.user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info.id,
        }

        res = self.client.post(
            ORDER_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_own_order_detail_patch_normal_user_reject(self):
        """
        Tests if normal user can't patch own order detail
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        order = self.model.objects.create(**mock_order)

        order_detail_url = get_order_detail_url(
            [order]  # obtain the url of created order
        )

        payload = {
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ]
        }

        res = self.client.patch(
            order_detail_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_order_detail_put_normal_user_reject(self):
        """
        Tests if normal user can't put own order detail
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        order = self.model.objects.create(**mock_order)

        order_detail_url = get_order_detail_url(
            [order]  # obtain the url of created order
        )

        payload = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ],
            "shipping_info": shipping_info,
        }

        res = self.client.put(
            order_detail_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_order_detail_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete own order detail
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        order = self.model.objects.create(**mock_order)

        order_detail_url = get_order_detail_url(
            [order]  # obtain the url of created order
        )

        res = self.client.delete(
            order_detail_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperusersOrdersAPITests(TestCase):
    """
    Tests orders by private superuser
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()  # order model

        main_user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.main_user = get_user_model().objects.create_superuser(
            **main_user_data  # create main user
        )

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com"  # create user for order
        )

        category = Category.objects.create(
            title="TestCategory"  # create category for product
        )
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(
            **self.mock_product  # create product for order
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(
            **self.mock_shipping_info  # create shipping info for order
        )

        self.mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        self.order = self.model.objects.create(**self.mock_order)

    def test_order_list_get_superuser_successful(self):
        """
        Tests if superuser can see order list
        """
        res = self.client.get(
            ORDER_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.order.id)

        self.assertIn("results", res.data)
        self.assertIn("data", res.data)

        self.assertEqual(res.data["results"], 1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_list_get_user_id_filter_superuser_successful(self):
        """
        Tests if superuser can see order list with user id filter
        """
        user = get_user_model().objects.create_user(email="newusertest@test.com")

        mock_order = {
            "buyer": user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        new_order = self.model.objects.create(**mock_order)

        user_filter_url = get_filter_url("user", str(user.id))

        res = self.client.get(
            user_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, new_order.id)
        self.assertNotContains(res, self.order.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_list_get_offset_filter_superuser_successful(self):
        """
        Tests if superuser can see order list with offset filter
        """
        user = get_user_model().objects.create_user(email="newusertest@test.com")

        mock_order = {
            "buyer": user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        first_new_order = self.model.objects.create(**mock_order)
        second_new_order = self.model.objects.create(**mock_order)

        user_filter_url = get_filter_url("offset", "2")

        res = self.client.get(
            user_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertNotContains(res, self.order.id)
        self.assertContains(res, first_new_order.id)
        self.assertContains(res, second_new_order.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_list_get_limit_filter_superuser_successful(self):
        """
        Tests if superuser can see order list with limit filter
        """
        user = get_user_model().objects.create_user(email="newusertest@test.com")

        mock_order = {
            "buyer": user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        first_new_order = self.model.objects.create(**mock_order)
        second_new_order = self.model.objects.create(**mock_order)

        user_filter_url = get_filter_url("limit", "2")

        res = self.client.get(
            user_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.order.id)
        self.assertContains(res, first_new_order.id)
        self.assertNotContains(res, second_new_order.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_list_get_results_with_offset_filter_superuser_successful(self):
        """
        Tests if superuser can see order list correct results
        with offset filter
        """
        user = get_user_model().objects.create_user(email="newusertest@test.com")

        mock_order = {
            "buyer": user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        first_new_order = self.model.objects.create(**mock_order)
        second_new_order = self.model.objects.create(**mock_order)

        user_filter_url = get_filter_url("offset", "2")

        res = self.client.get(
            user_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertNotContains(res, self.order.id)
        self.assertContains(res, first_new_order.id)
        self.assertContains(res, second_new_order.id)

        self.assertEqual(res.data["results"], 3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_list_get_results_with_limit_filter_superuser_successful(self):
        """
        Tests if superuser can see order list correct results
        with limit filter
        """
        user = get_user_model().objects.create_user(email="newusertest@test.com")

        mock_order = {
            "buyer": user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }
        first_new_order = self.model.objects.create(**mock_order)
        second_new_order = self.model.objects.create(**mock_order)

        limit_filter_url = get_filter_url("limit", "2")

        res = self.client.get(
            limit_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.order.id)
        self.assertContains(res, first_new_order.id)
        self.assertNotContains(res, second_new_order.id)

        self.assertEqual(res.data["results"], 3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_detail_get_superuser_successful(self):
        """
        Tests if superuser can see order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        res = self.client.get(
            order_detail_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_own_order_list_post_superuser_successful(self):
        """
        Tests if superuser can post order list
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        payload = {
            "buyer": self.main_user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info.id,
        }

        res = self.client.post(
            ORDER_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_order_list_post_superuser_for_other_user_successful(self):
        """
        Tests if superuser can post in order list for other user
        """

        payload = {
            "buyer": self.user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info.id,
        }

        res = self.client.post(
            ORDER_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_own_order_detail_patch_superuser_successful(self):
        """
        Tests if superuser can patch own order detail
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        order = self.model.objects.create(**mock_order)

        order_detail_url = get_order_detail_url(
            [order]  # obtain the url of created order
        )

        payload = {
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ]
        }

        res = self.client.patch(
            order_detail_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_detail_patch_superuser_from_other_user_successful(self):
        """
        Tests if superuser can patch order detail from other user
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        payload = {
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ]
        }

        res = self.client.patch(
            order_detail_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_own_order_detail_put_superuser_successful(self):
        """
        Tests if superuser can put own order detail
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        order = self.model.objects.create(**mock_order)

        order_detail_url = get_order_detail_url(
            [order]  # obtain the url of created order
        )

        payload = {
            "buyer": self.main_user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ],
            "shipping_info": shipping_info.id,
        }

        res = self.client.put(
            order_detail_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_detail_put_superuser_from_other_user_successful(self):
        """
        Tests if superuser can put own order detail
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        payload = {
            "buyer": self.user.id,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 6}
            ],
            "shipping_info": self.shipping_info.id,
        }

        res = self.client.put(
            order_detail_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.order.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_own_order_detail_delete_super_user_successful(self):
        """
        Tests if superuser can delete own order detail
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(
            **mock_shipping_info  # create shipping info for order
        )

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        order = self.model.objects.create(**mock_order)

        order_detail_url = get_order_detail_url(
            [order]  # obtain the url of created order
        )

        res = self.client.delete(
            order_detail_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_order_detail_delete_superuser_from_other_user_successful(self):
        """
        Tests if superuser can delete order detail from other user
        """
        order_list = self.model.objects.all()
        order_detail_url = get_order_detail_url(order_list)

        res = self.client.delete(
            order_detail_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
