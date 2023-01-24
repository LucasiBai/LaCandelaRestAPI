import json

from rest_framework import serializers

from .meta import get_app_model, get_secondary_model

from db.models import Product


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
            "created_at",
            "products"
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
        products = validated_data.get("products", None)

        parsed_products = []
        for product in products:
            print(product)
            serializer = OrderProductSerializer(data=product)
            if serializer.is_valid():
                parsed_products.append(serializer.data)

        print(parsed_products)

        buyer = validated_data.get("buyer", None)
        shipping_info = validated_data.get("shipping_info")

        order = self.Meta.model.objects.create(buyer=buyer, shipping_info=shipping_info)
        order.create_order_products(parsed_products)

        return order

    def to_representation(self, instance):
        """
        Sets the order representation

        Args:
            instance: instance to format

        Returns:
            formatted instance
        """

        order_products = get_secondary_model().objects.filter(order=instance)

        format_data = {
            "id": instance.id,
            "buyer": instance.buyer.id,
            "shipping_info": instance.shipping_info.id,
            "created_at": instance.created_at
        }

        return format_data


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Order Product Serializer
    """

    class Meta:
        model = get_secondary_model()
        fields = ["product", "count"]

    def validated_product(self, value):
        print(value)
        return value

    def validated_count(self, value):
        print(value)
        return value
