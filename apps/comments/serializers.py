from rest_framework import serializers

from db.models import Comment, Order


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer
    """

    class Meta:
        model = Comment
        fields = [
            "user",
            "product",
            "subject",
            "content",
            "rate",
            "created_at",
        ]

    def validate_user(self, value):
        current_user = self.context.get("user", None)
        action = self.context.get("action", None)

        if action:
            if current_user.id != value.id and not current_user.is_superuser:
                raise serializers.ValidationError(
                    "Current user only can create his own comment"
                )

        return value

    def validate(self, attrs):
        action = self.context.get("action", None)

        if action:
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
