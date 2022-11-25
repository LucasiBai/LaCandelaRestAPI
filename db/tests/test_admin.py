from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from db.models import Comment, Category, Product


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
        Tests if category added can be updated
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
            "selled": 11,
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
        Tests if product added is listed
        """
        url = reverse("admin:db_product_change", args=[self.product.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_product_page(self):
        """
        Tests if product added is listed
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
            "selled": 11,
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
        Tests if comment added is listed
        """
        url = reverse("admin:db_comment_change", args=[self.comment.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200

    def test_create_comment_page(self):
        """
        Tests if comment added is listed
        """
        url = reverse("admin:db_comment_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Testing if status code is 200
