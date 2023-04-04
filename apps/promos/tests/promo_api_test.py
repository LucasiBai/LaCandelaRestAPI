import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from apps.promos.meta import get_app_model

PROMO_URL = reverse("api:promo-list")


def get_promo_detail_url(promo_instance: get_app_model()):
    """
    Gets detail url from entered instance

    Args:
        promo_instance(Promo): promo to get url

    Returns:
        promo instance url
    """
    return reverse("api:promo-detail", kwargs={"id": promo_instance.id})


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
            "images": ["www.testurl.com/image/1"],
            "href": "www.testurl.com/test-promo"
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
        promo_url = get_promo_detail_url(self.promo.id)
        res = self.client.get(promo_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertContains(res.data["id"], self.promo.id)
        self.assertContains(res.data["title"], self.promo.title)
