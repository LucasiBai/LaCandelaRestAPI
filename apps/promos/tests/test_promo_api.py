import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from apps.promos.meta import get_app_model

PROMO_URL = reverse("api:promo-list")  # promo API url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_promo_detail_url(promo_instance: get_app_model()):
    """
    Gets detail url from entered instance

    Args:
        promo_instance(Promo): promo to get url

    Returns:
        promo instance url
    """
    return reverse("api:promo-detail", kwargs={"pk": promo_instance.id})


class PublicPromoAPITests(TestCase):
    """
    Tests promo with public client
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        self.mock_promo = {
            "title": "Test Promo Title",
            "subtitle": "Test Promo Subtitle",
            "expiration": datetime.date(1997, 10, 19),
            "images": ["testurl.com/image/1"],
            "href": "testurl.com/test-promo"
        }

        self.promo = self.model.objects.create(**self.mock_promo)

    def test_promo_list_view_no_items_public_user_successful(self):
        """
        Tests if promo list view can be accessed by public user with no items
        """
        self.promo.delete()

        res = self.client.get(PROMO_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["message"], "Not found promos.")

    def test_promo_list_view_public_user_successful(self):
        """
        Tests if promo list view can be accessed by public user
        """
        res = self.client.get(PROMO_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.promo.title)

        self.assertIn("data", res.data)
        self.assertIn("results", res.data)

        self.assertEqual(res.data["results"], 1)

    def test_promo_retrieve_view_public_user_successful(self):
        """
        Tests if promo retrieve view can be accessed by public user
        """
        promo_url = get_promo_detail_url(self.promo)
        res = self.client.get(promo_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["id"], self.promo.id)
        self.assertEqual(res.data["title"], self.promo.title)
        self.assertEqual(res.data["subtitle"], self.promo.subtitle)
        self.assertEqual(res.data["expiration"], self.promo.expiration)
        self.assertEqual(res.data["images"], self.promo.images)
        self.assertEqual(res.data["href"], self.promo.href)

    def test_promo_retrieve_view_no_existent_promo_public_user_reject(self):
        """
        Tests if promo retrieve view can't render no existent promo by public user
        """
        promo_url = get_promo_detail_url(self.promo)

        self.promo.delete()

        res = self.client.get(promo_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_promo_list_view_create_public_user_reject(self):
        """
        Tests if public user can't create promo instance
        """

        payload = {
            **self.mock_promo,
            "title": "Test Post Promo"
        }

        res = self.client.post(PROMO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertFalse(self.model.objects.filter(title=payload["title"]).exists())

    def test_promo_retrieve_view_update_public_user_reject(self):
        """
        Tests if public user can't update promo instance
        """
        payload = {
            **self.mock_promo,
            "title": "Test Update Promo"
        }

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.put(promo_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.promo.refresh_from_db()

        self.assertNotEqual(self.promo.title, payload["title"])

    def test_promo_retrieve_view_partial_update_public_user_reject(self):
        """
        Tests if public user can't partial update promo instance
        """
        payload = {
            "title": "Test Update Promo"
        }

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.patch(promo_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.promo.refresh_from_db()

        self.assertNotEqual(self.promo.title, payload["title"])

    def test_promo_retrieve_view_delete_public_user_reject(self):
        """
        Tests if public user can't delete promo instance
        """
        promo_url = get_promo_detail_url(self.promo)

        res = self.client.delete(promo_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.promo.refresh_from_db()

        self.assertTrue(self.promo)


class PrivateUserPromoAPITests(TestCase):
    """
    Tests promo with normal user
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        # User Auth
        user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.user = get_user_model().objects.create_user(
            **user_data  # create main user
        )

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

        # Default Promo creation
        self.mock_promo = {
            "title": "Test Promo Title",
            "subtitle": "Test Promo Subtitle",
            "expiration": datetime.date(1997, 10, 19),
            "images": ["testurl.com/image/1"],
            "href": "testurl.com/test-promo"
        }

        self.promo = self.model.objects.create(**self.mock_promo)

    def test_promo_list_view_no_items_normal_user_successful(self):
        """
        Tests if promo list view can be accessed by normal user with no items
        """
        self.promo.delete()

        res = self.client.get(PROMO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["message"], "Not found promos.")

    def test_promo_list_view_normal_user_successful(self):
        """
        Tests if promo list view can be accessed by normal user
        """
        res = self.client.get(PROMO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.promo.title)

        self.assertIn("data", res.data)
        self.assertIn("results", res.data)

        self.assertEqual(res.data["results"], 1)

    def test_promo_retrieve_view_normal_user_successful(self):
        """
        Tests if promo retrieve view can be accessed by normal user
        """
        promo_url = get_promo_detail_url(self.promo)
        res = self.client.get(promo_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["id"], self.promo.id)
        self.assertEqual(res.data["title"], self.promo.title)
        self.assertEqual(res.data["subtitle"], self.promo.subtitle)
        self.assertEqual(res.data["expiration"], self.promo.expiration)
        self.assertEqual(res.data["images"], self.promo.images)
        self.assertEqual(res.data["href"], self.promo.href)

    def test_promo_retrieve_view_no_existent_promo_normal_user_reject(self):
        """
        Tests if promo retrieve view can't render no existent promo by normal user
        """
        promo_url = get_promo_detail_url(self.promo)

        self.promo.delete()

        res = self.client.get(promo_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_promo_list_view_create_normal_user_reject(self):
        """
        Tests if normal user can't create promo instance
        """

        payload = {
            **self.mock_promo,
            "title": "Test Post Promo"
        }

        res = self.client.post(PROMO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertFalse(self.model.objects.filter(title=payload["title"]).exists())

    def test_promo_retrieve_view_update_normal_user_reject(self):
        """
        Tests if normal user can't update promo instance
        """
        payload = {
            **self.mock_promo,
            "title": "Test Update Promo"
        }

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.put(promo_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.promo.refresh_from_db()

        self.assertNotEqual(self.promo.title, payload["title"])

    def test_promo_retrieve_view_partial_update_normal_user_reject(self):
        """
        Tests if normal user can't partial update promo instance
        """
        payload = {
            "title": "Test Update Promo"
        }

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.patch(promo_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.promo.refresh_from_db()

        self.assertNotEqual(self.promo.title, payload["title"])

    def test_promo_retrieve_view_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete promo instance
        """
        promo_url = get_promo_detail_url(self.promo)

        res = self.client.delete(promo_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.promo.refresh_from_db()

        self.assertTrue(self.promo)


class PrivateSuperuserPromoAPITests(TestCase):
    """
    Tests promo with superuser
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        # User Auth
        user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.user = get_user_model().objects.create_superuser(
            **user_data  # create main user
        )

        res_token = self.client.post(TOKEN_URL, user_data)  # get user token
        self.user_token = res_token.data["token"]

        # Default Promo creation
        self.mock_promo = {
            "title": "Test Promo Title",
            "subtitle": "Test Promo Subtitle",
            "expiration": datetime.date(1997, 10, 19),
            "images": ["testurl.com/image/1"],
            "href": "testurl.com/test-promo"
        }

        self.promo = self.model.objects.create(**self.mock_promo)

    def test_promo_list_view_no_items_superuser_successful(self):
        """
        Tests if promo list view can be accessed by superuser with no items
        """
        self.promo.delete()

        res = self.client.get(PROMO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["message"], "Not found promos.")

    def test_promo_list_view_superuser_successful(self):
        """
        Tests if promo list view can be accessed by superuser
        """
        res = self.client.get(PROMO_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res, self.promo.title)

        self.assertIn("data", res.data)
        self.assertIn("results", res.data)

        self.assertEqual(res.data["results"], 1)

    def test_promo_retrieve_view_superuser_successful(self):
        """
        Tests if promo retrieve view can be accessed by superuser
        """
        promo_url = get_promo_detail_url(self.promo)
        res = self.client.get(promo_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["id"], self.promo.id)
        self.assertEqual(res.data["title"], self.promo.title)
        self.assertEqual(res.data["subtitle"], self.promo.subtitle)
        self.assertEqual(res.data["expiration"], self.promo.expiration)
        self.assertEqual(res.data["images"], self.promo.images)
        self.assertEqual(res.data["href"], self.promo.href)

    def test_promo_retrieve_view_no_existent_promo_superuser_reject(self):
        """
        Tests if promo retrieve view can't render no existent promo by superuser
        """
        promo_url = get_promo_detail_url(self.promo)

        self.promo.delete()

        res = self.client.get(promo_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_promo_list_view_create_superuser_successful(self):
        """
        Tests if superuser can create promo instance
        """

        payload = {
            **self.mock_promo,
            "title": "Test Post Promo"
        }

        res = self.client.post(PROMO_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["id"], payload["id"])
        self.assertEqual(res.data["title"], payload["title"])
        self.assertEqual(res.data["subtitle"], payload["subtitle"])
        self.assertEqual(res.data["expiration"], payload["expiration"])
        self.assertEqual(res.data["images"], payload["images"])
        self.assertEqual(res.data["href"], payload["href"])

        self.assertTrue(self.model.objects.filter(title=payload["title"]).exists())

    def test_promo_retrieve_view_update_superuser_successful(self):
        """
        Tests if superuser can update promo instance
        """
        payload = {
            **self.mock_promo,
            "title": "Test Update Promo"
        }

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.put(promo_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.promo.refresh_from_db()

        self.assertEqual(self.promo.title, payload["title"])

    def test_promo_retrieve_view_partial_update_superuser_successful(self):
        """
        Tests if superuser can partial update promo instance
        """
        payload = {
            "title": "Test Update Promo"
        }

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.patch(promo_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.promo.refresh_from_db()

        self.assertEqual(self.promo.title, payload["title"])

    def test_promo_retrieve_view_delete_superuser_successful(self):
        """
        Tests if superuser can't delete promo instance
        """
        promo_id = self.promo.id

        promo_url = get_promo_detail_url(self.promo)

        res = self.client.delete(promo_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(pk=promo_id)
