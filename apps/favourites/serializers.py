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

    def create(self, validated_data):
        """
        Create a Fav item instance

        Args:
            validated_data: data of instance

        Returns:
            Created instance
        """
        product = validated_data.get("product", None)

        user = validated_data.get("user", None)

        instance = product.create_fav_to(user)

        return instance