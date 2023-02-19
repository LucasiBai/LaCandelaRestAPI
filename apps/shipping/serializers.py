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

    def to_representation(self, instance: get_app_model()):
        """
        Formats instance data

        Args:
            instance(ShippingInfo): instance to format

        Returns:
            formatted data
        """

        format_data = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "email": instance.user.email
            },
            "address": instance.address,
            "receiver": instance.receiver,
            "receiver_dni": instance.receiver_dni,
            "is_selected": instance.is_selected,
        }

        return format_data
