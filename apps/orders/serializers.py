from rest_framework import serializers

from .meta import get_app_model, get_secondary_model

from apps.api_root.utils import parse_json


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

    def validate(self, attrs):
        user = self.context.get("user", None)
        action = self.context.get("action", None)

        if action and action.lower() == "create":
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
        products = [parse_json(product) for product in products]

        buyer = validated_data.get("buyer", None)
        shipping_info = validated_data.get("shipping_info")

        order = self.Meta.model.objects.create(buyer=buyer, shipping_info=shipping_info)
        order.create_order_products(products)

        return order

    def update(self, instance, validated_data):
        """
        Update order and order product

        Args:
            instance(Order): instance to update
            validated_data(dict): data to update instance

        Returns:
            Updated instance
        """
        # Update order products
        products = validated_data.get("products", None)

        products = [parse_json(product) for product in products]

        instance.update_order_products(products)

        # Update shipping info
        shipping_info = validated_data.get("shipping_info", None)

        if shipping_info:
            instance.shipping_info = shipping_info
            instance.save()

        # Update buyer reject
        buyer = validated_data.get("buyer", None)

        if buyer and buyer.id != instance.buyer.id:
            raise serializers.ValidationError("Created order can't update buyer.")

        return instance

    def to_representation(self, instance):
        """
        Sets the order representation

        Args:
            instance: instance to format

        Returns:
            formatted instance
        """

        order_products = instance.get_order_products()
        order_products_serializer = OrderProductSerializer(order_products, many=True)

        format_data = {
            "id": instance.id,
            "buyer": {
                "id": instance.buyer.id,
                "email": instance.buyer.email,
            },
            "shipping_info": {
                "address": instance.shipping_info.address,
                "receiver": instance.shipping_info.receiver,
                "receiver_dni": instance.shipping_info.receiver_dni,
            },
            "created_at": instance.created_at,
            "products": order_products_serializer.data
        }

        return format_data


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Order Product Serializer
    """

    class Meta:
        model = get_secondary_model()
        fields = ["product", "count"]
