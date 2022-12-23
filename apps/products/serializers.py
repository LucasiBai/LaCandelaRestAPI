from rest_framework import serializers

from .meta import get_app_model
from .utils import get_rate_of


class ProductSerializer(serializers.ModelSerializer):
    """
    Products serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "title",
            "description",
            "price",
            "images",
            "stock",
            "category",
            "sold",
        ]
        extra_kwargs = {"id": {"read_only": True}}

    def to_representation(self, instance):
        """
        Custom representation of instance
        """

        rate = get_rate_of(instance)

        data = {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "price": instance.price,
            "images": instance.images,
            "stock": instance.stock,
            "category": instance.category.title,
            "sold": instance.sold,
            "rate": rate,
        }

        return data
