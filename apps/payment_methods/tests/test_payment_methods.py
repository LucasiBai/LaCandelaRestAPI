from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.payment_methods.utils import PaymentMethod, MercadoPagoMethod

from db.models import Cart, Product, Category


class PaymentMethodsTests(TestCase):
    def setUp(self):
        self.payment_model = PaymentMethod

        self.user = get_user_model().objects.create_user(email="testuser@test.com")

        self.cart = Cart.objects.create(user=self.user)

        category = Category.objects.create(title="TestCategory")

        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

        self.cart_item = self.cart.add_product(self.product, 5)

    def test_auto_mercado_pago_payment_method_successful(self):
        """
        Tests if generated payment method auto generate MercadoPagoMethod
        """

        payment_method = self.payment_model(cart=self.cart)

        self.assertEquals(str(payment_method.get_payment_method()), str(MercadoPagoMethod(cart=self.cart)))

    def test_payment_method_no_cart_reject(self):
        """
        Tests if state hasn't entered cart
        """

        with self.assertRaises(ValueError):
            payment_method = self.payment_model()

    def test_mercado_pago_get_preference_successful(self):
        """
        Tests if method can get mercado pago preference data with user cart
        """

        payment_method = self.payment_model(self.cart, MercadoPagoMethod)

        preference = payment_method.get_preference()

        self.assertIn("id", preference)
        self.assertIn("client_id", preference)
        self.assertIn("date_created", preference)
        self.assertIn("marketplace", preference)
        self.assertIn("payer", preference)
        self.assertIn("init_point", preference)

        preference_items = preference["items"]

        self.assertEquals(preference_items[0]["id"], self.product.id)
        self.assertEquals(preference_items[0]["quantity"], self.cart_item.count)

    # TODO: Create test of change_payment_method
