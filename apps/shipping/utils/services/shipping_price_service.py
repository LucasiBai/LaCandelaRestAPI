class ShippingPriceService:
    """Shipping price calculator service"""
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not ShippingPriceService.__instance:
            ShippingPriceService.__instance = object.__new__(cls)
        return ShippingPriceService.__instance

    # TODO: complete service with real functionality
    def get_price_from_zip_code(self, postal_code: int):
        """
        Calculates price from entered postal code

        Args:
            postal_code(int): destination zip code

        Returns:
            calculated price
        """
        return 1400

    def get_zip_code_of(self, address: str):
        """
        Gets the zip code of entered address

        Args:
            address(str): user address

        Returns:
            Zip code of entered address
        """

        return 5000
