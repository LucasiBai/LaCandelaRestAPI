from uuid import uuid4

from django.db import models
from django.db.utils import DataError, IntegrityError
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from simple_history.models import HistoricalRecords
from apps.shipping.utils.services.shipping_price_service import ShippingPriceService


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """Creates a user with email"""
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


class CommentManager(models.Manager):
    """
    Custom Comment Manager
    """

    @staticmethod
    def get_rate_avg_of(product=None):
        """
        Get rate avg of entered product
        """
        if not product:
            raise ValueError("Method must receive 'product'")

        rate_avg = Comment.objects.filter(product=product).aggregate(models.Avg('rate'))

        if rate_avg["rate__avg"]:
            return round(rate_avg["rate__avg"], 2)
        return 5


class Comment(models.Model):
    """
    Comment model
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    rate = models.FloatField()
    created_at = models.DateField(auto_now_add=True)

    objects = CommentManager()  # custom manager

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
    rate = models.FloatField(default=5.0, editable=False)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title

    def create_comment(self, user: UserAccount, subject: str, content: str, rate: float):
        """
        Creates a comment and update rate with avg
        """
        if not 0.1 <= rate <= 5:
            raise ValueError("Rate must be between 0.0 and 5.0")

        comment = Comment.objects.create(product=self, user=user, subject=subject, content=content, rate=rate)

        product_rate_avg = Comment.objects.get_rate_avg_of(self)

        self.rate = product_rate_avg
        self.save()

        return comment

    def create_fav_to(self, user: get_user_model()):
        """
        Creates a fav item to entered user

        Args:
            user(UserModel): user who want to create a fav

        Returns:
            Created fav item
        """

        user_fav_item, created = FavouriteItem.objects.get_or_create(user=user, product=self)

        return user_fav_item

    def delete_fav_to(self, user: get_user_model()):
        """
        Deletes existent fav item

        Args:
            user(UserModel): user who want to delete a fav

        Returns:
            None
        """
        user_fav_item = FavouriteItem.objects.filter(product=self, user=user).first()

        if not user_fav_item:
            raise FavouriteItem.DoesNotExist("Favourite Item must exist to be deleted.")

        user_fav_item.delete()


class ShippingInfoManager(models.Manager):
    """
    Shipping Info custom manager
    """
    ship_service = ShippingPriceService()

    def __set_is_selected_to(self, ship_info, is_selected: bool):
        """
        Changes entered shipping info state

        Args:
            ship_info(ShippingInfo): shipping info instance to update
            is_selected(bool): new state to instance

        Returns:
            updated instance
        """
        if not isinstance(is_selected, bool):
            raise ValueError("is_selected must be bool type")

        if ship_info.is_selected != is_selected:
            ship_info.is_selected = is_selected
            ship_info.save(using=self._db)

        return ship_info

    def create(self, *args, **kwargs):
        """
        Custom create instance method

        Returns:
            instance
        """
        ship_info = super().create(*args, **kwargs)

        user = kwargs.get("user", None)

        selected = self.get_selected_shipping_info(user)

        if not selected:
            self.__set_is_selected_to(ship_info, True)

        address_zip_code = self.ship_service.get_zip_code_of(ship_info.address)

        ship_info.ship_price = self.ship_service.get_price_from_zip_code(address_zip_code)
        ship_info.save(using=self._db)

        return ship_info

    def select_shipping_info(self, ship_info):
        """
        Selects a shipping info for user

        Args:
            ship_info: instance to select

        Returns:
            updated shipping info
        """
        user = ship_info.user

        current_selected = self.filter(user=user, is_selected=True).first()

        if current_selected:
            if ship_info.id == current_selected.id:
                return ship_info

            self.__set_is_selected_to(current_selected, False)

        self.__set_is_selected_to(ship_info, True)

        return ship_info

    def get_selected_shipping_info(self, user: UserAccount):
        """
        Gets the selected shipping info o entered user

        Args:
            user: user from which takes the shipping info

        Returns:
            selected shipping info
        """
        return self.filter(user=user, is_selected=True).first()


class ShippingInfo(models.Model):
    """
    ShippingInfo model
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    receiver_dni = models.IntegerField()
    is_selected = models.BooleanField(default=False)
    ship_price = models.DecimalField(default=0, max_digits=9, decimal_places=2)

    objects = ShippingInfoManager()

    class Meta:
        verbose_name = _("Shipping Information")
        verbose_name_plural = _("Shippings Information")

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{_('Shipping Info of')} {self.user.get_full_name()}"
        return f"{_('Shipping Info of')} {self.user.email}"


class OrderManager(models.Manager):
    """
    Order Model manager
    """

    def create(self, *args, **kwargs):
        """
        Custom order creation

        Returns:
            order instance
        """
        id = kwargs.get("id", None)
        buyer = kwargs.get("buyer", None)
        shipping_info = kwargs.get("shipping_info", None)

        instance = super().create(*args, id=id, buyer=buyer, shipping_info=shipping_info)

        products = kwargs.get("products", None)

        if products:
            instance.create_order_products(products)

        ship_price = kwargs.get("ship_price", None)

        if ship_price:
            instance.set_ship_amount(ship_price)
        elif shipping_info.ship_price > 0:
            instance.set_ship_amount(shipping_info.ship_price)

        return instance

    def discount_stock_of(self, order):
        """
        Discount stock of each product in order

        Args:
            order(Order): order to iterate

        Returns:
            None
        """
        order_products = order.get_order_products()

        for order_product in order_products:
            product = order_product.product
            product.stock = product.stock - order_product.count
            product.save()


class Order(models.Model):
    """
    Order model
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    buyer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    shipping_info = models.ForeignKey("ShippingInfo", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(default=0, max_digits=9, decimal_places=2)

    objects = OrderManager()

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        if self.buyer.first_name and self.buyer.last_name:
            return f"{_('Order of')} {self.buyer.get_full_name()}"
        return f"{_('Order of')} {self.buyer.email}"

    def get_order_products(self):
        """
        Search and gets order products list

        Returns:
            order products list
        """
        filtered_order_products = OrderProduct.objects.filter(order=self)

        if not filtered_order_products:
            raise DataError("Order instance don't have order products")

        return list(filtered_order_products)

    def create_order_products(self, product_list: list):
        """
        Creates order products related with current order

        Args:
            product_list(list<dict>): products to add in the order

        Returns:
            order products list
        """
        order_product_list = []

        for product in product_list:
            count = product.get("count", None)

            product_id = product.get("product", None)
            product = Product.objects.filter(pk=product_id).first()

            self.total_price += product.price * count  # update order price

            payload = {
                "count": count,
                "product": product,
                "order": self
            }
            order_product = OrderProduct.objects.create(**payload)  # create order product
            order_product.save()

            order_product_list.append(order_product)

        self.save()  # save model changes

        return order_product_list  # created order products

    def update_order_product(self, product, count: int):
        """
        Updates an order product

        Args:
            product(int): order product instance
            count(int): new count of order product

        Returns:
            Updated order product
        """
        order_product = OrderProduct.objects.filter(order=self, product=product).first()

        if not order_product:
            raise self.DoesNotExist("Order product doesn't exist")

        order_product.count = count
        order_product.save()

        return order_product

    def update_order_products(self, order_product_list: list):
        """
        Update the entered order product list

        Args:
            order_product_list(list<OrderProduct>): list of order products to update

        Returns:
            Updated order products
        """
        updated_order_products = []

        for product in order_product_list:
            updated = self.update_order_product(**product)
            updated_order_products.append(updated)

        return updated_order_products

    def set_ship_amount(self, ship_amount: int):
        """
        Updates total price with entered ship amount

        Args:
            ship_amount(int): ship price amount

        Returns:
            Updated order
        """

        self.total_price += ship_amount

        self.save()

        return self


class OrderProduct(models.Model):
    """
    Order Product model
    """
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    class Meta:
        verbose_name = _("Order Product")
        verbose_name_plural = _("Order Products")

    def __str__(self):
        return f"{self.count} of {self.product.title}"


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

    @staticmethod
    def get_cart_item_model():
        """
        Returns cart item model
        """
        return CartItem

    def get_products(self):
        """
        Gets own products
        """
        self.refresh_from_db()

        products = self.get_cart_item_model().objects.filter(cart=self)

        return products

    def get_total_price(self):
        """
        Calculates total price
        """
        self.refresh_from_db()

        cart_items = self.get_cart_item_model().objects.filter(cart=self)

        products_price = [item.product.price * item.count for item in cart_items]

        price = sum(products_price)

        return price

    def add_product(self, product: Product = None, count: int = None):
        """
        Creates a cart item and update total_items
        """
        self.refresh_products()  # refresh cart items stock

        if not product and not count:
            raise ValueError("Method must receive 'product' and 'count'")

        self.total_items += count  # updates total_item
        self.save()

        item_find = self.get_cart_item_model().objects.filter(cart=self, product=product).first()

        if count > product.stock or item_find and item_find.count + count > product.stock:
            raise ValueError("Item has insufficient stock")

        if item_find:
            item_find.set_count(item_find.count + count)
            return item_find

        payload = {"cart": self, "product": product, "count": count}

        cart_item = self.get_cart_item_model().objects.create(**payload)
        cart_item.save()

        return cart_item

    def remove_product(self, product: Product = None):
        """
        Deletes entered product and update total_items
        """
        if not product:
            raise ValueError("Method must receive a 'product'")

        cart_item = self.get_cart_item_model().objects.filter(cart=self, product=product).first()

        if not cart_item:
            raise self.DoesNotExist

        self.total_items -= cart_item.count
        self.save()

        cart_item.delete()

    def remove_all_products(self):
        """
        Deletes all cart products and update total_items
        """

        cart_items = self.get_cart_item_model().objects.filter(cart=self)

        if cart_items:
            cart_items.delete()

        self.total_items = 0
        self.save()

    def refresh_products(self):
        """
        Refreshes all cart items in cart if is necesary
        """

        cart_items = self.get_products()

        [cart_item.update_item_count() for cart_item in cart_items]


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
        self.save()

    def update_item_count(self):
        """
        Updates item count if stock is insufficient

        Returns:
            updated item
        """
        product = self.product
        product.refresh_from_db()

        if product.stock < self.count:
            self.set_count(product.stock)

        return self


class FavouriteItemManager(models.Manager):
    """
    Custom Manager to Favourite Item model
    """

    def create(self, *args, **kwargs):
        if self.filter(**kwargs).exists():
            raise IntegrityError("Favourite Item must no exist to create a new.")

        return super().create(*args, **kwargs)

    def get_user_fav(self, user: get_user_model()):
        """
        Gets fav products from entered user

        Args:
            user(UserModel): User who is searching favs

        Returns:
            List of user product favs
        """
        user_fav_list = self.filter(user=user)

        return user_fav_list


class FavouriteItem(models.Model):
    """
    Favourite Item model
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    objects = FavouriteItemManager()  # custom manager

    class Meta:
        verbose_name = "Favourite Item"
        verbose_name_plural = "Favourite Items"

    def __str__(self):
        """
        Returns:
            Model str representation
        """
        return f"{self.product} to {self.user}"


class Promo(models.Model):
    """
    Promo model
    """
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    expiration = models.DateField()
    images = ArrayField(
        models.URLField()
    )
    href = models.URLField()

    class Meta:
        verbose_name = "Promo"
        verbose_name_plural = "Promos"

    def __str__(self):
        """
        Returns:
            Model str representation
        """
        return self.title
