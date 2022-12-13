from rest_framework import serializers

from db.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Order model serializer
    """

    class Meta:
        model = Order
        fields = [
            "id",
            "buyer",
            "products",
            "shipping_info",
            "created_at",
        ]
