from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from .utils import send_reset_password_url_to


class UserAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "id": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
        }

    def create(self, validated_data):
        """
        Create a new user with create_user
        """
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Updates an user data and password
        """
        password = validated_data.pop("password", None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class ResetPasswordSerializer(serializers.Serializer):
    """
    Reset Password Email serializer
    """

    email = serializers.EmailField(min_length=5)

    class Meta:
        fields = ["email"]

    def validate_email(self, value):
        """
        Validates if exists user associated with entered email
        """
        user_exists = get_user_model().objects.filter(email=value).exists()

        if not user_exists:
            raise serializers.ValidationError(
                "Email entered must be associated with an user"
            )
        return value

    def save(self, **kwargs):
        """
        Sends an email for user to restart password
        """
        email = self.validated_data["email"]

        send_reset_password_url_to(email)


class ChangePasswordConfirmSerializer(serializers.Serializer):
    """
    Validates the entered data to change password
    """

    password = serializers.CharField(min_length=5, write_only=True)

    class Meta:
        fields = ["password"]

    def validate(self, attrs):

        token = self.context.get("token", None)
        encoded_pk = self.context.get("encoded_pk", None)

        if encoded_pk is None or token is None:
            raise serializers.ValidationError(
                "Missing token or encoded user primary key"
            )

        pk = urlsafe_base64_decode(encoded_pk).decode()
        self.user = get_user_model().objects.filter(pk=pk).first()

        if not self.user:
            raise serializers.ValidationError("Unknown primary key")

        if not PasswordResetTokenGenerator().check_token(self.user, token):
            raise serializers.ValidationError("Unknown token")

        return attrs

    def save(self, **kwargs):
        password = self.validated_data.pop("password", None)

        self.user.set_password(password)
        self.user.save()

        return self.user


class LoginTokenObtainSerializer(TokenObtainPairSerializer):
    """
    Serializer to obtain JWT
    """


class LoginTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Serializer to refresh JWT
    """
