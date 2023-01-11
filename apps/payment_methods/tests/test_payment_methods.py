from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.payment_methods.utils import PaymentMethods

from db.models import Cart, CartItem, Product


class PaymentMethodsTests(TestCase):
    def setUp(self):
        self.payment_model = PaymentMethods

        self.user = get_user_model().objects.create_user(email="testuser@test.com")

    def test_mercado_pago_get_preference_successful(self):
        """
        Tests if method can get mercado pago preference data with product
        """
        # TODO : create model method test
