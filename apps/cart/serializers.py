from rest_framework import serializers

from .meta import get_app_model, get_secondary_model
from db.models import Product


class CartSerializer(serializers.ModelSerializer):
    """
    Cart serializer
    """
    product = serializers.IntegerField()
    count = serializers.IntegerField()

    class Meta:
        model = get_app_model()
        fields = [
            "product",
            "count"
        ]

    def get_instance(self):
        """
        Gets cart instance

        Returns:
            current cart instance
        """
        return self.context.get("instance", None)

    def to_representation(self, instance):
        method = self.context.get("method", None)

        if method and method.upper() == "POST":
            item_serializer = CartItemSerializer(instance)

            return item_serializer.data

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

    def create(self, validated_data):
        """
        Creates Cart item related with current cart
        """
        product_pk = validated_data.get("product", None)
        product = Product.objects.filter(pk=product_pk).first()

        count = validated_data.get("count", None)

        instance = self.get_instance()

        payload = {
            "product": product,
            "count": count
        }

        try:
            cart_item = instance.add_product(**payload)

            return cart_item

        except:
            raise serializers.ValidationError("Item has insufficient stock.")


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
            "id": instance.id,
            "product": {
                "id": instance.product.id,
                "title": instance.product.title,
                "price": instance.product.price,
                "images": instance.product.images[0],
                "category": instance.product.category.title,
            },
            "count": instance.count,
        }

        return data
