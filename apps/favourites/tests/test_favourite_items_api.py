from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.favourites.meta import get_app_model

FAV_ITEM_LIST_URL = reverse("api:fav_item-list")  # fav item list url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


class PublicFavouriteItemAPITests(TestCase):
    """
    Tests cases of public user in Favourite Item Api
    """

    def setUp(self):
        self.client = APIClient()  # api client

        self.model = get_app_model()  # main app model

    def test_fav_item_list_view_public_user_reject(self):
        """
        Tests if public user can't access to fav item list view
        """

    def test_fav_item_retrieve_view_public_user_reject(self):
        """
        Tests if public user can't access to fav item retrieve view
        """

    def test_fav_item_list_create_public_user_reject(self):
        """
        Tests if public user can't create a fav item in fav item list view
        """

    def test_fav_item_retrieve_update_public_user_reject(self):
        """
        Tests if public user can't update a fav item in fav item retrieve view
        """

    def test_fav_item_retrieve_partially_update_public_user_reject(self):
        """
        Tests if public user can't partially update a fav item in fav item retrieve view
        """

    def test_fav_item_retrieve_delete_public_user_reject(self):
        """
        Tests if public user can't delete a fav item in fav item retrieve view
        """


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
