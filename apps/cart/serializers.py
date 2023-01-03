from rest_framework import serializers

from .meta import get_app_model


class CartSerializer(serializers.ModelSerializer):
    """
    Cart serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "user",
            "total_items",
            "last_modification",
        ]
