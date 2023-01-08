from uuid import uuid4

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

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
        """Creates a superuser with email"""

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

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
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
    price = models.DecimalField(max_digits=9, decimal_places=2)
    images = ArrayField(models.URLField(max_length=255))
    stock = models.PositiveIntegerField()
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    sold = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title


class ShippingInfo(models.Model):
    """
    ShippingInfo model
    """

    user = models.ForeignKey("UserAccount", on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    receiver_dni = models.IntegerField()

    class Meta:
        verbose_name = _("Shipping Information")
        verbose_name_plural = _("Shippings Information")

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{_('Shipping Info of')} {self.user.get_full_name()}"
        return f"{_('Shipping Info of')} {self.user.email}"


class Order(models.Model):
    """
    Order model
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    buyer = models.ForeignKey("UserAccount", on_delete=models.CASCADE)
    products = ArrayField(models.JSONField())
    shipping_info = models.ForeignKey("ShippingInfo", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        if self.buyer.first_name and self.buyer.last_name:
            return f"{_('Order of')} {self.buyer.get_full_name()}"
        return f"{_('Order of')} {self.buyer.email}"


class Cart(models.Model):
    """
    Cart model
    """

    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    total_items = models.IntegerField(default=0)
    last_modification = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return f"{str(self.user)}'s Cart"

    def get_products(self):
        """
        Gets own products
        """
        products = CartItem.objects.filter(cart=self)

        return products

    def get_total_price(self):
        """
        Calculates total price
        """

        cart_items = CartItem.objects.filter(cart=self)

        products_price = [item.product.price * item.count for item in cart_items]

        price = sum(products_price)

        return price

    def add_product(self, product: Product = None, count: int = None):
        """
        Creates a cart item and update total_items
        """
        if not product and not count:
            raise ValueError("Method must receive 'product' and 'count'")

        self.total_items += count

        item_find = CartItem.objects.filter(cart=self, product=product).first()

        if item_find:
            item_find.set_count(item_find.count + count)
            return item_find

        payload = {"cart": self, "product": product, "count": count}

        cart_item = CartItem.objects.create(**payload)

        return cart_item


class CartItem(models.Model):
    """
    Cart Item model
    """

    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    def __str__(self):
        return f"{self.product.title} to {self.cart.user.email}'s Cart"

    def set_count(self, count: int):
        self.count = count
