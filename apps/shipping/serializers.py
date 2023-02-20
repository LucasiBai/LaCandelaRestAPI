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

    def validate_user(self, value):
        """
        Validates if user is creating own shipping info or is superuser
        """
        current_user = self.context.get("user", None)

        if current_user and current_user.id != value.id and not current_user.is_superuser:
            raise serializers.ValidationError("The shipping info must contain the owner user.")

        return value

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
