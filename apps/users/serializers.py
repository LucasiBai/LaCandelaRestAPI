from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserAccountSerializer(serializers.ModelSerializer):
    """
    Serializers for User model
    """

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "id": {"read_only": True},
        }

    def create(self, validated_data):
        """
        Creata a new user with create_user
        """
        user = get_user_model().objects.create_user(**validated_data)
        return user
