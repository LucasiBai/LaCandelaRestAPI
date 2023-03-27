from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.favourites.meta import get_app_model

from db.models import Category, Product

FAV_ITEM_LIST_URL = reverse("api:fav_item-list")  # fav item list url
MY_LIST_URL = reverse("api:fav_item-get-my-list")  # fav item my-list action url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_fav_detail_url(fav_item: get_app_model()):
    """
    Gets the fav detail url of entered fav item
    """
    return reverse("api:fav_item-detail", kwargs={"pk": fav_item.id})


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return FAV_ITEM_LIST_URL + f"?{filter_name}={value}"


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

    def test_my_list_action_list_public_user_reject(self):
        """
        Tests if public user can't access to my-list api action
        """
        res = self.client.get(MY_LIST_URL)

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

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.fav_item.id)

    def test_own_fav_item_retrieve_view_format_normal_user_successful(self):
        """
        Tests if normal user can access to own fav item with correct format
        """
        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.fav_item.id)

        self.assertTrue(res.data["id"])

        # User format data
        self.assertTrue(res.data["user"])
        self.assertTrue(res.data["user"]["id"])
        self.assertTrue(res.data["user"]["email"])

        # Product format data
        self.assertTrue(res.data["product"])
        self.assertTrue(res.data["product"]["id"])
        self.assertTrue(res.data["product"]["title"])

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

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def test_my_list_action_list_normal_user_successful(self):
        """
        Tests if normal user can access to my-list api action and list fav items
        """
        # New user Fav item
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        fav_item = self.model.objects.create(product=self.product, user=new_user)

        res = self.client.get(MY_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        fav_list = [item["id"] for item in res.data["data"]]

        self.assertEqual(res.data["results"], 1)

        self.assertTrue(self.fav_item.id in fav_list)
        self.assertFalse(fav_item.id in fav_list)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_my_list_action_list_offset_filter_normal_user_successful(self):
        """
        Tests if normal user can access to my-list api action and filter list with offset
        """
        # New Product creation
        first_product = Product.objects.create(**{**self.mock_product, "title": "New First Title Product"})
        second_product = Product.objects.create(**{**self.mock_product, "title": "New Second Title Product"})

        # Fav item user creation
        first_fav = self.model.objects.create(user=self.user, product=first_product)
        second_fav = self.model.objects.create(user=self.user, product=second_product)

        filter_url = MY_LIST_URL + "?offset=2"

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        fav_list = [item["id"] for item in res.data["data"]]

        self.assertEqual(res.data["results"], 3)

        self.assertFalse(self.fav_item.id in fav_list)
        self.assertTrue(first_fav.id in fav_list)
        self.assertTrue(second_fav.id in fav_list)

    def test_my_list_action_list_limit_filter_normal_user_successful(self):
        """
        Tests if normal user can access to my-list api action and filter list with limit
        """
        # New Product creation
        first_product = Product.objects.create(**{**self.mock_product, "title": "New First Title Product"})
        second_product = Product.objects.create(**{**self.mock_product, "title": "New Second Title Product"})

        # Fav item user creation
        first_fav = self.model.objects.create(user=self.user, product=first_product)
        second_fav = self.model.objects.create(user=self.user, product=second_product)

        filter_url = MY_LIST_URL + "?limit=2"

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        fav_list = [item["id"] for item in res.data["data"]]

        self.assertEqual(res.data["results"], 3)

        self.assertTrue(self.fav_item.id in fav_list)
        self.assertTrue(first_fav.id in fav_list)
        self.assertFalse(second_fav.id in fav_list)

    def test_my_list_action_list_normal_user_no_items_successful(self):
        """
        Tests if normal user can access to my-list api action
        """
        self.fav_item.delete()

        res = self.client.get(MY_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("message", res.data)
        self.assertEqual(res.data["message"], "Not found fav items.")

    def test_my_list_action_create_normal_user_successful(self):
        """
        Tests if normal user can create item to my-list api action
        """
        mock_product = {**self.mock_product, "title": "New Product Test"}
        new_product = Product.objects.create(**mock_product)

        payload = {
            "product": new_product.id
        }

        res = self.client.post(MY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["product"]["id"], payload["product"])

        fav_item = self.model.objects.filter(user=self.user, product=new_product)
        self.assertTrue(fav_item.exists())

    def test_my_list_action_create_normal_user_existent_item_successful(self):
        """
        Tests if normal user can create post created item to my-list api action
        """
        payload = {
            "product": self.product.id
        }

        res = self.client.post(MY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["product"]["id"], payload["product"])

        fav_item = self.model.objects.filter(user=self.user, product=self.product)
        self.assertTrue(fav_item.exists())

    def test_my_list_action_create_normal_user_no_product_reject(self):
        """
        Tests if normal user can't create post no existent product to my-list api action
        """
        payload = {
            "product": self.product.id
        }

        self.product.delete()

        res = self.client.post(MY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_my_list_action_create_normal_user_no_product_param_reject(self):
        """
        Tests if normal user can't create post don't pass product to my-list api action
        """
        payload = {
            "user": self.user
        }

        res = self.client.post(MY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_list_detail_action_delete_normal_user_successful(self):
        """
        Tests if my list detail can delete item
        """
        fav_item_url = reverse("api:fav_item-get-my-list-detail", kwargs={"pk": self.fav_item.id})

        res = self.client.delete(fav_item_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        fav_list = self.model.objects.filter(user=self.user)

        self.assertFalse(fav_list)

    def test_my_list_detail_action_delete_normal_user_other_user_reject(self):
        """
        Tests if my list detail can't delete item from other user
        """
        # New user Fav item
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        fav_item = self.model.objects.create(product=self.product, user=new_user)

        fav_item_url = reverse("api:fav_item-get-my-list-detail", kwargs={"pk": fav_item.id})

        res = self.client.delete(fav_item_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        fav_list = self.model.objects.filter(user=new_user)

        self.assertTrue(fav_list)


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

    def test_fav_item_list_view_superuser_no_items_successful(self):
        """
        Tests if view returns a not found fav items message
        """
        self.fav_item.delete()

        res = self.client.get(FAV_ITEM_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("message", res.data)
        self.assertEqual(res.data["message"], "Not found fav items.")

    def test_fav_item_list_view_superuser_successful(self):
        """
        Tests if superuser can access to fav item list view
        """
        res = self.client.get(FAV_ITEM_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.fav_item.id)

        self.assertIn("data", res.data)
        self.assertIn("results", res.data)

        self.assertEqual(res.data["results"], 1)

    def test_fav_item_list_view_offset_filter_superuser_successful(self):
        """
        Tests if superuser can filter with offset fav item list view
        """
        # New Product creation
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        # New User creation
        new_user = get_user_model().objects.create_user(email="Testnewuser@email.com")

        # Fav Item Creation
        user_second_fav_item = self.model.objects.create(user=self.user, product=new_product)
        new_user_first_fav_item = self.model.objects.create(user=new_user, product=self.product)
        new_user_second_fav_item = self.model.objects.create(user=new_user, product=new_product)

        filter_url = get_filter_url("offset", 2)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 4)

        self.assertNotContains(res, self.fav_item.id)
        self.assertContains(res, user_second_fav_item.id)
        self.assertContains(res, new_user_first_fav_item.id)
        self.assertContains(res, new_user_second_fav_item.id)

    def test_fav_item_list_view_limit_filter_superuser_successful(self):
        """
        Tests if superuser can filter with limit fav item list view
        """
        # New Product creation
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        # New User creation
        new_user = get_user_model().objects.create_user(email="Testnewuser@email.com")

        # Fav Item Creation
        user_second_fav_item = self.model.objects.create(user=self.user, product=new_product)
        new_user_first_fav_item = self.model.objects.create(user=new_user, product=self.product)
        new_user_second_fav_item = self.model.objects.create(user=new_user, product=new_product)

        filter_url = get_filter_url("limit", 2)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 4)

        self.assertContains(res, self.fav_item.id)
        self.assertContains(res, user_second_fav_item.id)
        self.assertNotContains(res, new_user_first_fav_item.id)
        self.assertNotContains(res, new_user_second_fav_item.id)

    def test_fav_item_list_view_customer_id_filter_superuser_successful(self):
        """
        Tests if superuser can filter with customer_id fav item list view
        """
        # New Product creation
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        # New User creation
        new_user = get_user_model().objects.create_user(email="Testnewuser@email.com")

        # Fav Item Creation
        user_second_fav_item = self.model.objects.create(user=self.user, product=new_product)
        new_user_first_fav_item = self.model.objects.create(user=new_user, product=self.product)
        new_user_second_fav_item = self.model.objects.create(user=new_user, product=new_product)

        filter_url = get_filter_url("customer_id", self.user.id)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 2)

        self.assertContains(res, self.fav_item.id)
        self.assertContains(res, user_second_fav_item.id)
        self.assertNotContains(res, new_user_first_fav_item.id)
        self.assertNotContains(res, new_user_second_fav_item.id)

    def test_fav_item_list_view_product_id_filter_superuser_successful(self):
        """
        Tests if superuser can filter with product_id fav item list view
        """
        # New Product creation
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        # New User creation
        new_user = get_user_model().objects.create_user(email="Testnewuser@email.com")

        # Fav Item Creation
        user_second_fav_item = self.model.objects.create(user=self.user, product=new_product)
        new_user_first_fav_item = self.model.objects.create(user=new_user, product=self.product)
        new_user_second_fav_item = self.model.objects.create(user=new_user, product=new_product)

        filter_url = get_filter_url("product_id", self.product.id)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 2)

        self.assertContains(res, self.fav_item.id)
        self.assertNotContains(res, user_second_fav_item.id)
        self.assertContains(res, new_user_first_fav_item.id)
        self.assertNotContains(res, new_user_second_fav_item.id)

    def test_fav_item_retrieve_view_format_superuser_successful(self):
        """
        Tests if superuser can access to fav item with correct format
        """
        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.fav_item.id)

        self.assertTrue(res.data["id"])

        # User format data
        self.assertTrue(res.data["user"])
        self.assertTrue(res.data["user"]["id"])
        self.assertTrue(res.data["user"]["email"])

        # Product format data
        self.assertTrue(res.data["product"])
        self.assertTrue(res.data["product"]["id"])
        self.assertTrue(res.data["product"]["title"])

    def test_own_fav_item_retrieve_view_superuser_successful(self):
        """
        Tests if superuser can access to own fav item retrieve view
        """
        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.fav_item.id)

    def test_from_other_fav_item_retrieve_view_superuser_successful(self):
        """
        Tests if superuser can access to from other fav item retrieve view
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")

        fav_item = self.model.objects.create(product=self.product, user=new_user)

        retrieve_url = get_fav_detail_url(fav_item)
        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, fav_item.id)

    def test_own_fav_item_list_create_superuser_successful(self):
        """
        Tests if superuser can create an own fav item in fav item list view
        """
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "user": self.user.id,
            "product": new_product.id
        }

        res = self.client.post(FAV_ITEM_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertTrue(self.model.objects.filter(id=res.data["id"]).exists())

    def test_own_fav_item_list_create_existing_item_superuser_successful(self):
        """
        Tests if superuser can create an own existing fav item in fav item list view
        """
        payload = {
            "user": self.user.id,
            "product": self.product.id
        }

        res = self.client.post(FAV_ITEM_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertTrue(self.model.objects.filter(id=res.data["id"]).exists())

    def test_to_other_fav_item_list_create_superuser_successful(self):
        """
        Tests if superuser can create a fav item to others in fav item list view
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "user": new_user.id,
            "product": new_product.id
        }

        res = self.client.post(FAV_ITEM_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertTrue(self.model.objects.filter(id=res.data["id"]).exists())

    def test_own_fav_item_retrieve_update_superuser_reject(self):
        """
        Tests if superuser can't update an own fav item in fav item retrieve view
        """
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "user": self.user.id,
            "product": new_product.id  # param to update
        }

        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_from_other_fav_item_retrieve_update_superuser_reject(self):
        """
        Tests if superuser can't update a fav item from other in fav item retrieve view
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

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_own_fav_item_retrieve_partially_update_superuser_reject(self):
        """
        Tests if superuser can't partially update an own fav item in fav item retrieve view
        """
        new_product = Product.objects.create(**{**self.mock_product, "title": "New Title Product"})

        payload = {
            "product": new_product.id  # param to update
        }

        retrieve_url = get_fav_detail_url(self.fav_item)
        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_from_other_fav_item_retrieve_partially_update_superuser_reject(self):
        """
        Tests if superuser can't partially update a fav item from other in fav item retrieve view
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

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_own_fav_item_retrieve_delete_superuser_successful(self):
        """
        Tests if superuser can delete an own fav item in fav item retrieve view
        """
        retrieve_url = get_fav_detail_url(self.fav_item)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_from_other_fav_item_retrieve_delete_superuser_successful(self):
        """
        Tests if superuser can delete a fav item from other in fav item retrieve view
        """
        # New user Fav item
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        fav_item = self.model.objects.create(product=self.product, user=new_user)

        retrieve_url = get_fav_detail_url(fav_item)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
