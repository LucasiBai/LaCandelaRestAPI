from uuid import uuid4

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from db.models import Comment, Category, Product, ShippingInfo, Order, Cart, CartItem, OrderProduct, FavouriteItem


class UserModelAdminTest(TestCase):
    """
    Tests User admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(
            email="testuser@mitest.com",
            password="pass1234",
            first_name="TestUserName",  # Creating Normal User
        )

    def test_user_listed(self):
        """
        Tests if the users added were listed
        """
        url = reverse("admin:db_useraccount_changelist")
        res = self.client.get(url)

        self.assertContains(
            res, self.user.first_name  # Testing if normal user is listed
        )
        self.assertContains(res, self.user.email)

        self.assertContains(
            res, self.super_user.email  # Testing if super user is listed
        )

    def test_user_change_page(self):
        """
        Tests if the change page work
        """
        url = reverse("admin:db_useraccount_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_user_page(self):
        """
        Tests if the create user page work
        """
        url = reverse("admin:db_useraccount_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class CategoryModelAdminTest(TestCase):
    """
    Tests Category admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.category = Category.objects.create(title="Test Admin Category")

    def test_category_listed(self):
        """
        Tests if category added is listed
        """
        url = reverse("admin:db_category_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.category.title)

    def test_category_change_page(self):
        """
        Tests if category added can be edited
        """
        url = reverse("admin:db_category_change", args=[self.category.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_category_page(self):
        """
        Tests if can add category
        """
        url = reverse("admin:db_category_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class ProductModelAdminTest(TestCase):
    """
    Tests Product admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.category = Category.objects.create(title="Test Admin Category")

        product_payload = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }

        self.product = Product.objects.create(**product_payload)

    def test_product_listed(self):
        """
        Tests if product added is listed
        """
        url = reverse("admin:db_product_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.product.title)
        self.assertContains(res, self.category.title)
        self.assertContains(res, self.product.price)
        self.assertContains(res, self.product.stock)

    def test_product_change_page(self):
        """
        Tests if product added can be edited
        """
        url = reverse("admin:db_product_change", args=[self.product.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_product_page(self):
        """
        Tests if can create product
        """
        url = reverse("admin:db_product_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class CommentModelAdminTest(TestCase):
    """
    Tests Comment admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        category = Category.objects.create(title="Test Admin Category")

        self.user = get_user_model().objects.create_user(email="test@test.com")

        product_payload = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }

        self.product = Product.objects.create(**product_payload)

        comment_payload = {
            "user": self.user,
            "product": self.product,
            "subject": "Test subject",
            "content": "Test content",
            "rate": 2.5,
        }

        self.comment = Comment.objects.create(**comment_payload)

    def test_comment_listed(self):
        """
        Tests if comment added is listed
        """
        url = reverse("admin:db_comment_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.product.title)
        self.assertContains(res, self.user.email)

    def test_comment_change_page(self):
        """
        Tests if comment added can be edited
        """
        url = reverse("admin:db_comment_change", args=[self.comment.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_comment_page(self):
        """
        Tests if can create comment
        """
        url = reverse("admin:db_comment_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class ShippingInfoModelAdminTest(TestCase):
    """
    Tests Shipping info admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

        self.shipping_info = ShippingInfo.objects.create(**mock_shipping_info)

    def test_shipping_info_listed(self):
        """
        Tests if shipping info added is listed
        """
        url = reverse("admin:db_shippinginfo_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.shipping_info.id)
        self.assertContains(res, str(self.shipping_info))
        self.assertContains(res, self.user.email)

    def test_shipping_info_change_page(self):
        """
        Tests if shipping info added is can be edited
        """
        url = reverse("admin:db_shippinginfo_change", args=[self.shipping_info.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_shipping_info_page(self):
        """
        Tests if shipping info added can be created
        """
        url = reverse("admin:db_shippinginfo_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class OrderProductModelAdminTest(TestCase):
    """
    Tests Order product admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        # Product creation
        self.category = Category.objects.create(title="TestCategory")
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        self.product = Product.objects.create(**self.mock_product)

        # Order creation
        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(**self.mock_shipping_info)

        self.mock_order = {
            "id": uuid4(),
            "buyer": self.user,
            "shipping_info": self.shipping_info,
        }
        self.order = Order.objects.create(**self.mock_order)

        # Order product creation
        mock_order_product = {
            "product": self.product,
            "count": 5,
            "order": self.order,
        }
        self.order_product = OrderProduct.objects.create(**mock_order_product)

    def test_order_product_listed(self):
        """
        Tests if order product added is listed
        """
        url = reverse("admin:db_orderproduct_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.order_product.id)
        self.assertContains(res, str(self.order_product))

    def test_order_product_change_page(self):
        """
        Tests if order product added is can be edited
        """
        url = reverse("admin:db_orderproduct_change", args=[self.order_product.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_order_product_page(self):
        """
        Tests if order product added can be created
        """
        url = reverse("admin:db_orderproduct_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class OrderModelAdminTest(TestCase):
    """
    Tests Order admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating superuser
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        category = Category.objects.create(title="Test Admin Category")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

        mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(**mock_shipping_info)

        mock_order = {
            "id": uuid4(),
            "buyer": self.user,
            "shipping_info": self.shipping_info,
        }
        self.order = Order.objects.create(**mock_order)

    def test_order_listed(self):
        """
        Tests if order added is listed
        """
        url = reverse("admin:db_order_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.order.id)
        self.assertContains(res, str(self.order))

    def test_order_change_page(self):
        """
        Tests if order added can be edited
        """
        url = reverse("admin:db_order_change", args=[self.order.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_order_page(self):
        """
        Tests if can add order
        """
        url = reverse("admin:db_order_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class CartItemModelAdminTest(TestCase):
    """
    Tests Cart Item admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        self.cart = Cart.objects.create(user=self.user)

        category = Category.objects.create(title="Test Admin Category")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

        self.mock_cart_item = {"cart": self.cart, "product": self.product, "count": 5}
        self.cart_item = CartItem.objects.create(**self.mock_cart_item)

    def test_cart_item_listed(self):
        """
        Tests if cart item added is listed
        """
        url = reverse("admin:db_cartitem_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.cart_item.id)
        self.assertContains(res, self.cart_item.cart.user)
        self.assertContains(res, self.cart_item.product.title)

    def test_cart_item_change_page(self):
        """
        Tests if cart_item added can be edited
        """
        url = reverse("admin:db_cartitem_change", args=[self.cart_item.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_cart_item_page(self):
        """
        Tests if can add cart item
        """
        url = reverse("admin:db_cartitem_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class CartModelAdminTest(TestCase):
    """
    Tests Cart admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        self.cart = Cart.objects.create(user=self.user)

    def test_cart_listed(self):
        """
        Tests if cart added is listed
        """
        url = reverse("admin:db_cart_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.cart.id)

    def test_cart_change_page(self):
        """
        Tests if cart added can be edited
        """
        url = reverse("admin:db_cart_change", args=[self.cart.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_cart_page(self):
        """
        Tests if admin can add cart
        """
        url = reverse("admin:db_cart_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200


class FavouriteItemModelAdminTest(TestCase):
    """
    Tests Favourite items admin
    """

    def setUp(self):
        """
        Set up method
        """
        self.client = Client()

        self.super_user = get_user_model().objects.create_superuser(
            email="testadmin@mitest.com", password="pass1234"  # Creating super user
        )
        self.client.force_login(self.super_user)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        category = Category.objects.create(title="Test Admin Category")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        self.product = Product.objects.create(**mock_product)

        self.fav_item = FavouriteItem.objects.create(user=self.user, product=self.product)

    def test_fav_items_listed(self):
        """
        Tests if fav item added is listed
        """
        url = reverse("admin:db_favouriteitem_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.fav_item.id)
        self.assertContains(res, self.product.title)
        self.assertContains(res, self.user.email)

    def test_fav_items_change_page(self):
        """
        Tests if fav item added can be edited
        """
        url = reverse("admin:db_favouriteitem_change", args=[self.fav_item.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_fav_item_page(self):
        """
        Tests if admin can add cart
        """
        url = reverse("admin:db_favouriteitem_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200
