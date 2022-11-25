from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext as _

from simple_history.models import HistoricalRecords


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """Creates an user with email"""
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(email=email, **kwargs)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **kwargs):
        """Creates a super user with email"""

        if not email or not password:
            raise ValueError("Users must have an email address and password")

        user = self.create_user(email, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """Personalized model of User"""

    email = models.EmailField(max_length=255, unique=True)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    user_history = HistoricalRecords()

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def get_full_name(self):
        return f"{self.first_name}, {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email


class Category(models.Model):
    """
    Category model
    """

    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Comment model
    """

    user = models.ForeignKey("UserAccount", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    rate = models.FloatField()
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return self.subject


class Product(models.Model):
    """
    Product model
    """

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.PositiveBigIntegerField()
    images = ArrayField(models.CharField(max_length=255))
    stock = models.PositiveIntegerField()
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    selled = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title
