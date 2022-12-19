from rest_framework import serializers

from db.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Category model serializer
    """

    class Meta:
        model = Category
        fields = ["parent", "title"]
