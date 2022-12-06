from rest_framework import serializers

from db.models import Product, Comment


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
            "sold",
        ]
        extra_kwargs = {"id": {"read_only": True}}

    def to_representation(self, instance):
        """
        Custom representation of instance
        """

        comments_of_product = Comment.objects.filter(product=instance)

        if comments_of_product:
            rate = round(
                sum(comment.rate for comment in comments_of_product)
                / len(comments_of_product),
                2,
            )

        data = {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "price": instance.price,
            "images": instance.images,
            "stock": instance.stock,
            "category": instance.category.title,
            "sold": instance.sold,
            "rate": rate if comments_of_product else 5.00,
        }

        return data
