from rest_framework import serializers

from .meta import get_app_model


class OrderSerializer(serializers.ModelSerializer):
    """
    Order model serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "buyer",
            "products",
            "shipping_info",
            "created_at",
        ]

    def validate(self, attrs):
        user = self.context.get("user", None)
        action = self.context.get("action", None)

        if action == "create":
            if not user:
                raise serializers.ValidationError(
                    "User must be authenticated to post data"
                )

            buyer = attrs.get("buyer", None)
            shipping_info = attrs.get("shipping_info", None)

            if (
                shipping_info.user.id == user.id and buyer.id == user.id
            ) or user.is_superuser:
                return attrs

            raise serializers.ValidationError(
                "Order buyer and shipping info must have current user"
            )

        else:
            return attrs
