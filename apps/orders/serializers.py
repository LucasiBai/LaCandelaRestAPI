from rest_framework import serializers

from .meta import get_app_model


class OrderSerializer(serializers.ModelSerializer):
    """
    Order model serializer
    """
    products = serializers.ListField(allow_null=False, allow_empty=False)

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "buyer",
            "shipping_info",
            "products",
            "created_at",
        ]

    def validate_products(self, value: list):
        """
        Validates product data

        Args:
            value(list): value to validate

        Returns:
            validated data
        """

        return value

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

    def create(self, validated_data):
        """
        Create order with entered products

        Args:
            validated_data: entered data

        Returns:
            created instance
        """
        products = validated_data
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Sets the order representation

        Args:
            instance: instance to format

        Returns:
            formatted instance
        """
        return super().to_representation(instance)
