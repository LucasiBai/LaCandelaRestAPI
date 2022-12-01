from uuid import uuid4

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


from db.models import Category, Product, Comment, Order, ShippingInfo


class UserModelTest(TestCase):
    """
    Tests custom user model
    """

    def test_create_user_with_email_successful(self):
        """
        Tests if it is possible to create a user with email address
        """
        email = "test@mitest.com"
        pwd = "testpassword"

        user = get_user_model().objects.create_user(email=email, password=pwd)

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(pwd))

    def test_new_user_email_normalized(self):
        """
        Tests if email for new user is normalized
        """
        email = "test@MiTest.cOm"

        user = get_user_model().objects.create_user(email=email)

        self.assertEqual(user.email, email.lower())

    def test_create_superuser_with_email_successful(self):
        """
        Tests if it is possible to create a superuser with email address
        """
        email = "test@mitest.com"
        pwd = "testpassword"

        user = get_user_model().objects.create_superuser(email=email, password=pwd)
        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(pwd))

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_with_email_exception(self):
        """
        Tests if the create user raise an error when it has'nt email address
        """

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user(email=None)

    def test_create_superuser_password_exception(self):
        """
        Tests if the create superuser raise an error when it has'nt password
        """
        email = "test@mitest.com"

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_superuser(email=email, password=None)

    def test_create_superuser_email_exception(self):
        """
        Tests if the create superuser raise an error when it has'nt password
        """

        pwd = "testpassword"

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_superuser(email=None, password=pwd)


class CategoryModelTest(TestCase):
    """
    Tests Category model
    """

    def test_create_category_successful(self):
        """
        Tests if can create a Category
        """
        category = Category.objects.create(title="TestCategory")

        self.assertEqual("TestCategory", category.title)

        self.assertEqual("TestCategory", str(category))

    def test_create_existing_category_reject(self):
        """
        Tests if can't create an existing category
        """
        Category.objects.create(title="TestCategory")

        with self.assertRaises(IntegrityError):
            Category.objects.create(title="TestCategory")


class ProductModelTest(TestCase):
    """
    Tests Product model
    """

    def setUp(self):
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
            "selled": 11,
        }

    def test_create_product_successful(self):
        """
        Tests if its possible create product
        """

        product = Product.objects.create(**self.mock_product)

        self.assertEqual(product.title, self.mock_product["title"])
        self.assertEqual(product.price, self.mock_product["price"])
        self.assertEqual(product.description, self.mock_product["description"])
        self.assertEqual(product.images[0], self.mock_product["images"][0])
        self.assertEqual(product.category, self.category)

        self.assertEqual(self.mock_product["title"], str(product))

    def test_create_existing_product_reject(self):
        """
        Tests if can't create an existing product
        """

        Product.objects.create(**self.mock_product)

        with self.assertRaises(IntegrityError):
            Product.objects.create(**self.mock_product)


class ShippingInfoModelTest(TestCase):
    """
    Tests Shipping info model
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

    def test_create_shipping_info_successful(self):
        """
        Tests if model can create shipping info
        """
        shipping_info = ShippingInfo.objects.create(**self.mock_shipping_info)

        self.assertEqual(shipping_info.user, self.user)
        self.assertEqual(shipping_info.address, self.mock_shipping_info["address"])

        self.assertEqual(
            f"Shipping Info of {self.user.get_full_name()}", str(shipping_info)
        )


class OrderModelTest(TestCase):
    """
    Tests order model
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(email="testemail@test.com")

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
            "selled": 11,
        }
        self.product = Product.objects.create(**self.mock_product)

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
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }

    def test_create_order_successful(self):
        """
        Tests if model can create an order
        """
        order = Order.objects.create(**self.mock_order)

        self.assertEqual(order.id, self.mock_order["id"])
        self.assertEqual(order.buyer, self.user)
        self.assertEqual(order.products, self.mock_order["products"])
        self.assertEqual(order.shipping_info, self.shipping_info)
        self.assertTrue(order.created_at)

        self.assertEqual(f"Order of {order.buyer.get_full_name()}", str(order))

    def test_create_existing_order_reject(self):
        """
        Tests if can't create an existing order
        """

        Order.objects.create(**self.mock_order)

        with self.assertRaises(IntegrityError):
            Order.objects.create(**self.mock_order)


class CommentModelTest(TestCase):
    """
    Tests Comment model
    """

    def setUp(self):
        category = Category.objects.create(title="TestCategory")

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
            "selled": 11,
        }

        self.product = Product.objects.create(**mock_product)  # create product

        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testPass"  # create user
        )

    def test_create_comment_successful(self):
        """
        Tests if can create a comment
        """

        mock_comment = {
            "user": self.user,
            "product": self.product,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        comment = Comment.objects.create(**mock_comment)

        self.assertEqual(self.user, comment.user)
        self.assertEqual(self.product, comment.product)
        self.assertEqual(mock_comment["subject"], comment.subject)

        self.assertEqual(mock_comment["subject"], str(comment))

        self.assertTrue(comment.created_at)
