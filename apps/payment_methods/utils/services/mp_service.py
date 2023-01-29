import mercadopago

from core.settings.base import MERCADO_PAGO_CONFIG


class MPService:
    """
    Mercado Pago Service
    """
    __instance = None
    sdk = mercadopago.SDK(MERCADO_PAGO_CONFIG["ACCESS_TOKEN"])

    def __new__(cls, *args, **kwargs):
        if not MPService.__instance:
            MPService.__instance = object.__new__(cls)
        return MPService.__instance

    def get_preference(self, pref_config: dict):
        """
        Gets preference of buy in mercado pago sdk

        Args:
            pref_config(dict): preference data config

        Returns:
            Obtained preference
        """

        preference: dict = self.sdk.preference().create(pref_config)

        return preference
