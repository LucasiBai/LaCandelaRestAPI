from rest_framework.serializers import ModelSerializer

from .meta import get_app_model


class PromoSerializer(ModelSerializer):
    """
    Promo Api Serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "title",
            "subtitle",
            "expiration",
            "images",
            "href",
        ]
