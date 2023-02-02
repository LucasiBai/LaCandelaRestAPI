from django.test import TestCase

from apps.payment_methods.utils.order_creation import OrderCreation, MercadoPagoMethod


class OrderMethodsTests(TestCase):
    def setUp(self):
        self.order_creation_model = OrderCreation

    def test_auto_mercado_pago_order_creation_successful(self):
        """
        Tests if generated order creation auto generate MercadoPagoMethod
        """

        order_creation = self.order_creation_model()

        self.assertEquals(str(order_creation.get_order_method()), str(MercadoPagoMethod()))

    # TODO: Create test of change_order_method
