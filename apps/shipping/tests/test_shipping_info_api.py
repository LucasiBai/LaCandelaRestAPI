from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from apps.shipping.meta import get_app_model

SHIPPING_INFO_URL = reverse("api:shipping_info-list")  # shipping info API url

MY_INFO_URL = reverse("api:shipping_info-my-info")  # my shipping info API url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_shipping_info_url(shipping_instance: get_app_model()):
    """
    Gets shipping info entered instance url

    Args:
        shipping_instance: instance from which the url is obtained

    Returns:
        obtained url
    """
    return reverse("api:shipping_info-detail", kwargs={"pk": shipping_instance.id})


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return SHIPPING_INFO_URL + f"?{filter_name}={value}"


class PublicShippingInfoAPITests(TestCase):
    """
    Tests Shipping Info Api with public client
    """

    def setUp(self):
        self.client = APIClient()
        self.model = get_app_model()

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = self.model(**self.mock_shipping_info)

    def test_ship_info_list_view_public_user_get_reject(self):
        """
        Tests if public user can't list shipping info api
        """
        res = self.client.get(SHIPPING_INFO_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_get_reject(self):
        """
        Tests if public user can't retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.get(retrieve_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_info_list_view_public_user_get_reject(self):
        """
        Tests if public user can't list my info api
        """
        res = self.client.get(MY_INFO_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_list_view_public_user_post_reject(self):
        """
        Tests if public user can't post in list shipping info api
        """
        payload = {
            "user": self.user.id,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

        res = self.client.post(SHIPPING_INFO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_put_reject(self):
        """
        Tests if public user can't put retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = {
            "user": self.user.id,
            "address": "Updated Test address",
            "receiver": "test receiver name",
            "receiver_dni": 87654321,
        }

        res = self.client.put(retrieve_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_patch_reject(self):
        """
        Tests if public user can't patch retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = {
            "address": "Updated Test address",
            "receiver_dni": 87654321,
        }

        res = self.client.patch(retrieve_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ship_info_retrieve_view_public_user_delete_reject(self):
        """
        Tests if public user can't delete retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.delete(retrieve_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserShippingInfoAPITests(TestCase):
    """
    Tests Shipping Info Api with private user
    """

    def setUp(self):
        self.client = APIClient()
        self.model = get_app_model()

        user_data = {
            "email": "testemail@test.com",
            "password": "testPassword123"
        }
        self.user = get_user_model().objects.create_user(
            **user_data, first_name="Test", last_name="Testi"
        )

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = self.model.objects.create(**self.mock_shipping_info)

    def test_ship_info_list_view_normal_user_get_reject(self):
        """
        Tests if normal user can't list shipping info api
        """
        res = self.client.get(SHIPPING_INFO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ship_info_retrieve_view_normal_user_get_reject(self):
        """
        Tests if normal user can't retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ship_info_list_view_normal_user_post_successful(self):
        """
        Tests if normal user can post in list shipping info api and is selected
        """
        payload = {
            "user": self.user.id,
            "address": "New Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

        res = self.client.post(SHIPPING_INFO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["user"]["id"], payload["user"])
        self.assertEqual(res.data["receiver_dni"], payload["receiver_dni"])

        self.assertTrue(res.data["is_selected"])

        self.shipping_info.refresh_from_db()
        self.assertFalse(self.shipping_info.is_selected)

    def test_ship_info_list_view_normal_user_post_to_other_user_reject(self):
        """
        Tests if normal user can't post to other user in list shipping info api
        """
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")

        payload = {
            "user": new_user.id,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

        res = self.client.post(SHIPPING_INFO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ship_info_retrieve_view_normal_user_put_reject(self):
        """
        Tests if normal user can't put retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = {
            "user": self.user.id,
            "address": "Updated Test address",
            "receiver": "test receiver name",
            "receiver_dni": 87654321,
        }

        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ship_info_retrieve_view_normal_user_patch_reject(self):
        """
        Tests if normal user can't patch retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = self.mock_shipping_info = {
            "address": "Updated Test address",
            "receiver_dni": 87654321,
        }

        res = self.client.patch(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ship_info_retrieve_view_normal_user_delete_reject(self):
        """
        Tests if normal user can't delete retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_my_info_action_view_normal_user_get_successful(self):
        """
        Tests if api has my info action and list current user shipping info
        """
        # creation of own shipping info
        mock_ship_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        own_ship_info = self.model.objects.create(**mock_ship_info)

        # creation of ship info from other
        new_user = get_user_model().objects.create_user(email="newusertest@test.com")
        mock_ship_info["user"] = new_user
        other_user_ship_info = self.model.objects.create(**mock_ship_info)

        res = self.client.get(MY_INFO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 2)

        self.assertContains(res, self.shipping_info.id)
        self.assertContains(res, own_ship_info.id)
        self.assertNotContains(res, other_user_ship_info.id)

        self.assertTrue(res.data["data"][0]["is_selected"])

    def test_my_info_action_view_normal_user_filter_limit_successful(self):
        """
        Tests if api has my info action and list current user shipping info filtered with limit
        """
        # creation of own shipping info
        mock_ship_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        first_ship_info = self.model.objects.create(**mock_ship_info)

        mock_ship_info["receiver_dni"] = 11223344
        second_ship_info = self.model.objects.create(**mock_ship_info)

        filter_url = MY_INFO_URL + "?limit=2"

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 3)

        self.assertContains(res, self.shipping_info.receiver_dni)
        self.assertContains(res, first_ship_info.receiver_dni)
        self.assertNotContains(res, second_ship_info.receiver_dni)

    def test_my_info_action_view_normal_user_filter_offset_successful(self):
        """
        Tests if api has my info action and list current user shipping info filtered with offset
        """
        # creation of own shipping info
        mock_ship_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        first_ship_info = self.model.objects.create(**mock_ship_info)

        mock_ship_info["receiver_dni"] = 11223344
        second_ship_info = self.model.objects.create(**mock_ship_info)

        filter_url = MY_INFO_URL + "?offset=2"

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 3)

        self.assertNotContains(res, self.shipping_info.receiver_dni)
        self.assertContains(res, first_ship_info.receiver_dni)
        self.assertContains(res, second_ship_info.receiver_dni)

    def test_my_info_action_view_normal_user_filter_is_selected_true_successful(self):
        """
        Tests if api has my info action and list current user shipping info filtered with is_selected true
        """
        # creation of own shipping info
        mock_ship_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        first_ship_info = self.model.objects.create(**mock_ship_info)

        mock_ship_info["receiver_dni"] = 11223344
        second_ship_info = self.model.objects.create(**mock_ship_info)

        filter_url = MY_INFO_URL + "?is_selected=true"

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 1)

        self.assertContains(res, self.shipping_info.receiver_dni)
        self.assertNotContains(res, first_ship_info.receiver_dni)
        self.assertNotContains(res, second_ship_info.receiver_dni)

    def test_my_info_action_view_normal_user_filter_is_selected_false_successful(self):
        """
        Tests if api has my info action and list current user shipping info filtered with is_selected false
        """
        # creation of own shipping info
        mock_ship_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        first_ship_info = self.model.objects.create(**mock_ship_info)

        mock_ship_info["receiver_dni"] = 11223344
        second_ship_info = self.model.objects.create(**mock_ship_info)

        filter_url = MY_INFO_URL + "?is_selected=false"

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], 2)

        self.assertNotContains(res, self.shipping_info.receiver_dni)
        self.assertContains(res, first_ship_info.receiver_dni)
        self.assertContains(res, second_ship_info.receiver_dni)

    def test_my_info_action_view_normal_user_select_ship_info_successful(self):
        """
        Tests if api has my info action and selects entered ship_info
        """
        # creation of own shipping info
        mock_ship_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        own_ship_info = self.model.objects.create(**mock_ship_info)

        self.assertFalse(own_ship_info.is_selected)

        payload = {
            "select": own_ship_info.id
        }

        res = self.client.post(MY_INFO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        own_ship_info.refresh_from_db()
        self.assertEqual(res.data["id"], own_ship_info.id)
        self.assertEqual(res.data["is_selected"], own_ship_info.is_selected)
        self.assertTrue(own_ship_info.is_selected)

        self.assertEqual(self.shipping_info.user.id, own_ship_info.user.id)

        self.shipping_info.refresh_from_db()
        self.assertFalse(self.shipping_info.is_selected)

    def test_my_info_action_view_normal_user_select_ship_info_to_other_user_reject(self):
        """
        Tests if api has my info action and can't select entered ship_info if it is from other user
        """
        new_user = get_user_model().objects.create_user(email="newtest_user@test.com")  # new user creation

        # creation of new user shipping info
        mock_ship_info = {
            **self.mock_shipping_info,
            "receiver_dni": 87654321,
            "user": new_user
        }
        self.model.objects.create(**mock_ship_info)
        second_ship_info = self.model.objects.create(**mock_ship_info)

        self.assertFalse(second_ship_info.is_selected)

        payload = {
            "select": second_ship_info.id
        }

        res = self.client.post(MY_INFO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        second_ship_info.refresh_from_db()
        self.assertFalse(second_ship_info.is_selected)


class PrivateSuperuserShippingInfoAPITests(TestCase):
    """
    Tests Shipping Info Api with private superuser
    """

    def setUp(self):
        self.client = APIClient()
        self.model = get_app_model()

        # superuser credential creation
        superuser_data = {
            "email": "testemail@superuser.com",
            "password": "testPassword123"
        }

        self.super_user = get_user_model().objects.create_superuser(**superuser_data)

        res_token = self.client.post(TOKEN_URL, superuser_data)  # get user token
        self.user_token = res_token.data["token"]

        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = self.model.objects.create(**self.mock_shipping_info)

    def test_ship_info_list_view_superuser_get_successful(self):
        """
        Tests if superuser can list shipping info api
        """
        res = self.client.get(SHIPPING_INFO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data["data"]), 1)
        self.assertEqual(res.data["results"], 1)

    def test_ship_info_list_view_superuser_filter_limit_successful(self):
        """
        Tests if superuser can list shipping info api with limit filter
        """
        mock_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        first_ship_info = self.model.objects.create(**mock_info)

        mock_info["receiver_dni"] = 11223344
        second_ship_info = self.model.objects.create(**mock_info)

        filter_url = get_filter_url("limit", 2)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.shipping_info.receiver_dni)
        self.assertContains(res, first_ship_info.receiver_dni)
        self.assertNotContains(res, second_ship_info.receiver_dni)

        self.assertEqual(res.data["results"], 3)

    def test_ship_info_list_view_superuser_filter_offset_successful(self):
        """
        Tests if superuser can list shipping info api with offset filter
        """
        mock_info = {**self.mock_shipping_info, "receiver_dni": 87654321}
        first_ship_info = self.model.objects.create(**mock_info)

        mock_info["receiver_dni"] = 11223344
        second_ship_info = self.model.objects.create(**mock_info)

        filter_url = get_filter_url("offset", 2)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertNotContains(res, self.shipping_info.receiver_dni)
        self.assertContains(res, first_ship_info.receiver_dni)
        self.assertContains(res, second_ship_info.receiver_dni)

        self.assertEqual(res.data["results"], 3)

    def test_ship_info_list_view_superuser_filter_user_id_successful(self):
        """
        Tests if superuser can list shipping info api with user_id filter
        """
        first_ship_info = self.model.objects.create(**self.mock_shipping_info)

        # new user data creation
        new_user = get_user_model().objects.create_user(email="testnewuser@test.com")
        mock_ship_info = {**self.mock_shipping_info, "user": new_user}
        new_user_ship_info = self.model.objects.create(**mock_ship_info)

        filter_url = get_filter_url("user_id", self.user.id)

        res = self.client.get(filter_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.shipping_info.id)
        self.assertContains(res, first_ship_info.id)
        self.assertNotContains(res, new_user_ship_info.id)

        self.assertEqual(res.data["results"], 2)

    def test_ship_info_retrieve_view_superuser_get_successful(self):
        """
        Tests if superuser can retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.get(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["id"], self.shipping_info.id)

    def test_ship_info_list_view_superuser_post_to_other_user_successful(self):
        """
        Tests if superuser can post to other user in list shipping info api
        """
        payload = {
            "user": self.user.id,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

        res = self.client.post(SHIPPING_INFO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["user"]["id"], payload["user"])
        self.assertEqual(res.data["receiver_dni"], payload["receiver_dni"])

    def test_ship_info_retrieve_view_superuser_put_to_other_user_successful(self):
        """
        Tests if superuser can put retrieve to other user shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = {
            "user": self.user.id,
            "address": "Updated Test address",
            "receiver": "test receiver name",
            "receiver_dni": 87654321,
        }

        res = self.client.put(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["receiver_dni"], payload["receiver_dni"])

        self.shipping_info.refresh_from_db()
        self.assertEqual(self.shipping_info.receiver_dni, payload["receiver_dni"])
        self.assertEqual(self.shipping_info.address, payload["address"])

    def test_ship_info_retrieve_view_superuser_patch_to_other_user_successful(self):
        """
        Tests if superuser can patch retrieve to other user shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        payload = self.mock_shipping_info = {
            "address": "Updated Test address",
            "receiver_dni": 87654321,
        }

        res = self.client.patch(retrieve_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["receiver_dni"], payload["receiver_dni"])

        self.shipping_info.refresh_from_db()
        self.assertEqual(self.shipping_info.receiver_dni, payload["receiver_dni"])
        self.assertEqual(self.shipping_info.address, payload["address"])

    def test_ship_info_retrieve_view_superuser_delete_reject(self):
        """
        Tests if superuser can't delete retrieve shipping info api
        """
        retrieve_url = get_shipping_info_url(self.shipping_info)

        res = self.client.delete(retrieve_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
