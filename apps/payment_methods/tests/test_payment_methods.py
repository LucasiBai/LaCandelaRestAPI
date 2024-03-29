from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.payment_methods.utils.payment_methods import PaymentMethod, MercadoPagoMethod
from apps.payment_methods.utils.models.payment_strategy import PaymentStrategyInterface

from db.models import Cart, Product, Category, ShippingInfo


class MockPayMethod(PaymentStrategyInterface):
    """
    Mock Pay Method
    """

    def __init__(self, cart: Cart):
        self.__cart = cart

    def get_preference(self):
        return "Test Mock Reference"


class PaymentMethodsTests(TestCase):
    def setUp(self):
        self.payment_model = PaymentMethod

        self.user = get_user_model().objects.create_user(email="testuser@test.com")

        mock_user_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.ship_info = ShippingInfo.objects.create(**mock_user_shipping_info)

        self.cart = Cart.objects.create(user=self.user)

        self.category = Category.objects.create(title="TestCategory")

        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 11,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

        self.cart_item = self.cart.add_product(self.product, 5)

    def test_context_change_payment_method_succesfull(self):
        """
        Tests if method change to entered payment method
        """

        context = self.payment_model(self.cart, MercadoPagoMethod)

        self.assertEquals(str(context.get_payment_method()), str(MercadoPagoMethod(self.cart)))

        context.change_payment_method(MockPayMethod)

        self.assertEqual("Test Mock Reference", context.get_preference())

    def test_context_change_payment_method_no_param_reject(self):
        """
        Tests if method raise an error with no param
        """
        context = self.payment_model(self.cart, MercadoPagoMethod)

        with self.assertRaises(ValueError):
            context.change_payment_method()

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
            self.payment_model()

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
        self.assertIn("date_of_expiration", preference)
        self.assertIn("total_price", preference)

        preference_items = preference["items"]

        self.assertEquals(preference_items[0]["id"], str(self.product.id))
        self.assertEquals(preference_items[0]["quantity"], self.cart_item.count)
        self.assertEqual(preference["total_price"], self.cart.get_total_price() + self.ship_info.ship_price)

    def test_mercado_pago_get_preference_insufficient_stock_update_stock_reject(self):
        """
        Tests if method raise an error when product has insufficient stock
        and update all
        """
        # Product creation
        mock_product = {
            "title": "New Test title",
            "description": "Test description",
            "price": 11,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 6,
            "category": self.category,
            "sold": 11,
        }
        new_product = Product.objects.create(**mock_product)

        self.cart.add_product(new_product, 5)  # adding new product to cart

        # stock updating
        self.product.stock = 4
        self.product.save()

        new_product.stock = 3
        new_product.save()

        payment_method = self.payment_model(self.cart, MercadoPagoMethod)

        with self.assertRaises(ValueError):
            payment_method.get_preference()

        cart_products = self.cart.get_products()

        self.assertEqual(cart_products[0].count, 4)
        self.assertEqual(cart_products[1].count, 3)

    def test_mercado_pago_get_preference_date_of_expiration_successful(self):
        """
        Tests if method returns the correct date of expiration
        """

        payment_method = self.payment_model(self.cart, MercadoPagoMethod)

        preference = payment_method.get_preference()

        estimated_date = (datetime.now() + timedelta(days=3)).strftime(
            "%Y-%m-%d")

        self.assertEquals(preference["date_of_expiration"][:10], estimated_date)
