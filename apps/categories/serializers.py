from rest_framework import serializers

from .meta import get_app_model


class CategorySerializer(serializers.ModelSerializer):
    """
    Category model serializer
    """

    class Meta:
        model = get_app_model()
        fields = ["id", "parent", "title"]

    def to_representation(self, instance):
        """
        Returns parent categories with its subcategories
        """
        action = self.context.get("action", None)

        if action == "list" or not instance.parent:
            category_data = {
                "id": instance.id,
                "title": instance.title,
                "subcategories": [],
            }
            sub_categories = self.Meta.model.objects.exclude(parent=None)

            for sub_category in sub_categories:
                if sub_category.parent == instance:
                    sub_category_data = {
                        "id": sub_category.id,
                        "title": sub_category.title,
                    }

                    category_data["subcategories"].append(sub_category_data)

            return category_data

        else:
            category_data = {
                "id": instance.id,
                "title": instance.title,
                "parent": instance.parent.title,
            }
            return category_data
