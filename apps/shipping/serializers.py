from rest_framework import serializers

from .meta import get_app_model


class ShippingInfoSerializer(serializers.ModelSerializer):
    """
    Shipping Info Serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "user",
            "address",
            "receiver",
            "receiver_dni",
            "is_selected",
        ]
