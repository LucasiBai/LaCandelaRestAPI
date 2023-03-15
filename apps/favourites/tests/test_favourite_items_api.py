from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.favourites.meta import get_app_model

from db.models import Category, Product

FAV_ITEM_LIST_URL = reverse("api:fav_item-list")  # fav item list url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_fav_detail_url(fav_item: get_app_model()):
    """
    Gets the fav detail url of entered fav item
    """
    return reverse("api:order-detail", kwargs={"pk": fav_item.id})


class PublicFavouriteItemAPITests(TestCase):
    """
    Tests cases of public user in Favourite Item Api
    """

    def setUp(self):
        self.client = APIClient()  # api client

        self.model = get_app_model()  # main app model

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

        self.fav_item = self.model.objects.create(user=self.user, product=self.product)

    def test_fav_item_list_view_public_user_reject(self):
        """
        Tests if public user can't access to fav item list view
        """
        res = self.client.get(FAV_ITEM_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fav_item_retrieve_view_public_user_reject(self):
        """
        Tests if public user can't access to fav item retrieve view
        """
        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.get(retrieve_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fav_item_list_create_public_user_reject(self):
        """
        Tests if public user can't create a fav item in fav item list view
        """
        payload = {
            "user": self.user.id,
            "product": self.product.id
        }

        res = self.client.post(FAV_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fav_item_retrieve_update_public_user_reject(self):
        """
        Tests if public user can't update a fav item in fav item retrieve view
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")

        payload = {
            "user": new_user.id,
            "product": self.product.id
        }

        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.put(retrieve_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fav_item_retrieve_partially_update_public_user_reject(self):
        """
        Tests if public user can't partially update a fav item in fav item retrieve view
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")

        payload = {
            "user": new_user.id,
        }

        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.patch(retrieve_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fav_item_retrieve_delete_public_user_reject(self):
        """
        Tests if public user can't delete a fav item in fav item retrieve view
        """
        retrieve_url = get_fav_detail_url(self.fav_item)

        res = self.client.delete(retrieve_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserFavouriteItemAPITests(TestCase):
    """
    Tests cases of normal user in Favourite Item Api
    """

    def setUp(self):
        self.client = APIClient()  # api client

        self.model = get_app_model()  # main app model

        # User Auth

        user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.user = get_user_model().objects.create_user(
            **user_data  # create main user
        )

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

        # Product Creation
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

        # Fav Item Instance
        self.fav_item = self.model.objects.create(user=self.user, product=self.product)

    def test_fav_item_list_view_normal_user_reject(self):
        """
        Tests if normal user can't access to fav item list view
        """
        res = self.client.get(FAV_ITEM_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_fav_item_retrieve_view_normal_user_successful(self):
        """
        Tests if normal user can access to own fav item retrieve view
        """
        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_from_other_fav_item_retrieve_view_normal_user_reject(self):
        """
        Tests if normal user can't access to from other fav item retrieve view
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")

        fav_item = self.model.objects.create(product=self.product, user=new_user)

        retrieve_url = get_fav_detail_url(fav_item)
        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_fav_item_list_create_normal_user_reject(self):
        """
        Tests if normal user can't create an own fav item in fav item list view
        """
        payload = {
            "user": self.user.id,
            "product": self.product.id
        }

        res = self.client.post(FAV_ITEM_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_to_other_fav_item_list_create_normal_user_reject(self):
        """
        Tests if normal user can't create a fav item to others in fav item list view
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")

        payload = {
            "user": new_user.id,
            "product": self.product.id
        }

        res = self.client.post(FAV_ITEM_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_fav_item_retrieve_update_normal_user_reject(self):
        """
        Tests if normal user can't update an own fav item in fav item retrieve view
        """
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "user": self.user.id,
            "product": new_product.id  # param to update
        }

        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_from_other_fav_item_retrieve_update_normal_user_reject(self):
        """
        Tests if normal user can't update a fav item from other in fav item retrieve view
        """
        # New user Fav item
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        fav_item = self.model.objects.create(product=self.product, user=new_user)

        # New Product creation
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "user": new_user.id,
            "product": new_product.id  # param to update
        }

        retrieve_url = get_fav_detail_url(fav_item)
        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_fav_item_retrieve_partially_update_normal_user_reject(self):
        """
        Tests if normal user can't partially update an own fav item in fav item retrieve view
        """
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "product": new_product.id  # param to update
        }

        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_from_other_fav_item_retrieve_partially_update_normal_user_reject(self):
        """
        Tests if normal user can't partially update a fav item from other in fav item retrieve view
        """
        # New user Fav item
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        fav_item = self.model.objects.create(product=self.product, user=new_user)

        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "product": new_product.id  # param to update
        }

        retrieve_url = get_fav_detail_url(fav_item)
        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_fav_item_retrieve_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete an own fav item in fav item retrieve view
        """
        retrieve_url = get_fav_detail_url(self.fav_item)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_from_other_fav_item_retrieve_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete a fav item from other in fav item retrieve view
        """
        # New user Fav item
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        fav_item = self.model.objects.create(product=self.product, user=new_user)

        retrieve_url = get_fav_detail_url(fav_item)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # TODO: Test my-list api action


class PrivateSuperuserFavouriteItemAPITests(TestCase):
    """
    Tests cases of superuser in Favourite Item Api
    """

    def setUp(self):
        self.client = APIClient()  # api client

        self.model = get_app_model()  # main app model

        # User Auth
        user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.user = get_user_model().objects.create_superuser(
            **user_data  # create main user
        )

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

    # TODO: create tests for superuser in Favourite Item