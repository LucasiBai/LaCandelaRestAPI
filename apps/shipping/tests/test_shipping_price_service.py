from django.test import TestCase

from apps.shipping.utils.services.shipping_price_service import ShippingPriceService


class ShippingPriceServiceTests(TestCase):
    """
    Shipping price service test
    """

    def setUp(self):
        self.service = ShippingPriceService()

    def test_service_get_price_from_zip_code(self):
        """
        Tests if service can calculate price from zip code
        """
        price = self.service.get_price_from_zip_code(5000)

        self.assertTrue(price)

        self.assertEqual(price, 1400)
