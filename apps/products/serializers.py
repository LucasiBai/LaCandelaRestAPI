from rest_framework import serializers

from db.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Products serializer
    """

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "images",
            "stock",
            "category",
            "selled",
        ]
        extra_kwargs = {"id": {"read_only": True}}
