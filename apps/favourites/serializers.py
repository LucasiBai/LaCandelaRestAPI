from rest_framework import serializers

from .meta import get_app_model


class FavouriteItemsSerializer(serializers.ModelSerializer):
    """
    Favourite Item model serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "user",
            "product"
        ]
