from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from apps.cart.meta import get_app_model

from db.models import CartItem


def get_cart_detail_url(cart_instance):
    """
    Gets entered cart detail url
    """
    return reverse("api:cart-detail", kwargs={"pk": cart_instance.id})


class PublicCartApiTests(TestCase):
    """
    Tests Cart Api from public api
    """

    def setUp(self):
        self.client = APIClient()

        self.model = get_app_model()

        self.user = get_user_model().objects.create_user(
            email="testuser@test.com"  # create user
        )

        self.cart = self.model.objects.create(user=self.user)
