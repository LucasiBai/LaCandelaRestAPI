from rest_framework import serializers

from .meta import get_app_model


class ShippingInfoSerializer(serializers.ModelSerializer):
    """
    Shipping Info Serializer
    """

    class Meta:
        model = get_app_model()
        fields = [
            "id",
            "user",
            "address",
            "receiver",
            "receiver_dni",
            "is_selected",
        ]

    def create(self, validated_data):
        """
        Create shipping info with validated data

        Args:
            validated_data: data of shipping info

        Returns:
            created instance
        """
        instance = self.Meta.model.objects.create(**validated_data)

        self.Meta.model.objects.select_shipping_info(instance)

        return instance

    def validate_user(self, value):
        """
        Validates if user is creating own shipping info or is superuser
        """
        current_user = self.context.get("user", None)

        if current_user and current_user.id != value.id and not current_user.is_superuser:
            raise serializers.ValidationError("The shipping info must contain the owner user.")

        return value

    def to_representation(self, instance: get_app_model()):
        """
        Formats instance data

        Args:
            instance(ShippingInfo): instance to format

        Returns:
            formatted data
        """

        format_data = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "email": instance.user.email
            },
            "address": instance.address,
            "receiver": instance.receiver,
            "receiver_dni": instance.receiver_dni,
            "is_selected": instance.is_selected,
        }

        return format_data


class MyInfoSerializer(serializers.ModelSerializer):
    select = serializers.IntegerField()

    class Meta:
        model = get_app_model()
        fields = [
            "select"
        ]

    def validate_select(self, value):
        """
        Validates if shipping info exists

        Args:
            value: shipping info id

        Returns:
            value if it exists
        """
        user = self.context.get("user", None)

        query = self.Meta.model.objects.filter(id=value)

        if not query.exists():
            raise serializers.ValidationError("Shipping info does not exist.")

        if query.first().user.id != user.id:
            raise serializers.ValidationError("Can't update shipping info that is not yours.")

        self.instance = query.first()

        return value

    def select_instance(self):
        """
        Selects shipping info in validated data

        Returns:
            selected instance
        """
        ship_instance = self.instance

        selected_instance = self.Meta.model.objects.select_shipping_info(ship_instance)

        return selected_instance

    def save(self, **kwargs):
        """
        Selects entered instance
        """
        self.select_instance()

    def to_representation(self, validated_data):
        """
        Formats instance data

        Args:
            validated_data(OrderDict): data with select id

        Returns:
            formatted data
        """
        instance = self.instance

        format_data = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "email": instance.user.email
            },
            "address": instance.address,
            "receiver": instance.receiver,
            "receiver_dni": instance.receiver_dni,
            "is_selected": instance.is_selected,
        }

        return format_data
