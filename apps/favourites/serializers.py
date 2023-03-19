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

    def to_representation(self, instance: get_app_model()):
        """
        Formats instance data

        Args:
            instance: instance with data

        Returns:
            Formatted instance
        """
        format_data = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "email": instance.user.email
            },
            "product": {
                "id": instance.product.id,
                "title": instance.product.title,
            }
        }

        return format_data
