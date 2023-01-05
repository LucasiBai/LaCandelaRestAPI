from rest_framework import serializers

from .meta import get_app_model, get_secondary_model


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

    def to_representation(self, instance):
        item_serializer = CartItemSerializer(instance.get_products(), many=True)

        data = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "email": instance.user.email,
            },
            "total_items": instance.total_items,
            "total_price": instance.get_total_price(),
            "last_modification": instance.last_modification,
            "items": item_serializer.data,
        }

        return data


class CartItemSerializer(serializers.ModelSerializer):
    """
    Cart Item serializer
    """

    class Meta:
        model = get_secondary_model()
        fields = [
            "cart",
            "product",
            "count",
        ]

    def to_representation(self, instance):
        data = {
            "product": {
                "id": instance.id,
                "title": instance.product.title,
                "price": instance.product.price,
                "images": instance.product.images[0],
                "category": instance.product.category.title,
            },
            "count": instance.count,
        }

        return data
