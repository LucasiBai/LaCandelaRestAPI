from rest_framework import serializers

from .meta import get_app_model
from db.models import Order


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "user",
            "product",
            "subject",
            "content",
            "rate",
            "created_at",
        ]

    def validate_user(self, value):
        """
        Validates if user is the request user
        """
        current_user = self.context.get("user", None)
        action = self.context.get("action", None)

        if action and action == "create":
            if current_user.id != value.id and not current_user.is_superuser:
                raise serializers.ValidationError(
                    "Current user only can create his own comment"
                )

        return value

    def validate_rate(self, value):
        """
        Validates if entered rate can't be negative or greater than 5.0
        """
        if value > 5.0 or value < 0:
            raise serializers.ValidationError("Rate must be between 0.0 and 5.0")

        return value

    def validate(self, attrs):
        """
        Validates if request user has bought the product
        """
        action = self.context.get("action", None)

        if action and action == "create":
            product = attrs["product"]
            current_user = attrs["user"]
            user_orders = Order.objects.filter(buyer=current_user)

            bought_product = False

            for order in user_orders:
                for order_product in order.products:
                    if order_product["title"] == product.title:
                        bought_product = True

            if bought_product:
                return attrs
            raise serializers.ValidationError("User must have bought the product")

        else:
            return attrs

    def create(self, validated_data):
        """
        Creates a new comment with product create_comment
        """
        product = validated_data.get("product", None)

        data = validated_data
        data.pop("product")

        if not product:
            raise self.Meta.model.DoesNotExist

        instance = product.create_comment(**data)

        return instance
