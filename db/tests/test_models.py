from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


from db.models import Category, Product, Comment


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

    def test_create_category_succesful(self):
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

    def test_create_product_succcesful(self):
        """
        Tests if its posible create product
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
