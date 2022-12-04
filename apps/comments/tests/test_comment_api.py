from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from db.models import Comment, Product, Category, Order, ShippingInfo


COMMENT_LIST_URL = reverse("api:comment-list")  # comment list API url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_comment_detail_url(comment_list):
    """
    Gets the comment detail url of the first comment in list
    """
    return reverse("api:comment-detail", kwargs={"pk": comment_list[0].id})


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return reverse("api:comment-list") + f"?{filter_name}={value}"


class PublicCommentAPITest(TestCase):
    """
    Tests public comment api requests
    """

    def setUp(self):
        self.client = APIClient()  # API Client

        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",  # Mock product data
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": category,
            "selled": 11,
        }
        self.product = Product.objects.create(**mock_product)

        self.user = get_user_model().objects.create_user(email="test@test.com")

        self.mock_comment = {
            "user": self.user,
            "product": self.product,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        self.comment = Comment.objects.create(**self.mock_comment)

    def test_comment_list_get_public_successful(self):
        """
        Tests if public user can see comment list
        """
        res = self.client.get(COMMENT_LIST_URL)

        self.assertContains(res, self.comment)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_detail_get_public_successful(self):
        """
        Tests if public user can see comment detail
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)

        res = self.client.get(comment_url)

        self.assertContains(res, comment_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_list_post_public_reject(self):
        """
        Tests if public user can't create comment list
        """
        new_user = get_user_model().objects.create_user(email="newtest@test.com")

        payload = {
            "user": new_user,
            "product": self.product,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(COMMENT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_detail_patch_public_successful(self):
        """
        Tests if public user can't patch comment detail
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)

        payload = {"subject": "New Subject"}

        res = self.client.patch(comment_url, payload)
        self.comment.refresh_from_db()

        self.assertNotEqual(self.comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_detail_put_public_successful(self):
        """
        Tests if public user can't put comment detail
        """
