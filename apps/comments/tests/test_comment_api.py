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
    return COMMENT_LIST_URL + f"?{filter_name}={value}"


class PublicCommentAPITest(TestCase):
    """
    Tests public comment api requests
    """

    def setUp(self):
        self.client = APIClient()  # API Client

        self.category = Category.objects.create(title="TestCategory")
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
            "category": self.category,
            "sold": 11,
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

    def test_comment_list_user_id_filter_successful(self):
        """
        Tests if comment list can be filter by user id
        """
        new_user = get_user_model().objects.create_user(email="testnewuser@test.com")
        mock_comment = {
            "user": new_user,
            "product": self.product,
            "subject": "New Test comment subject",  # create new comment
            "content": "Test comment content",
            "rate": 4.3,
        }
        new_comment = Comment.objects.create(**mock_comment)  # created new comment

        user_filter_url = get_filter_url("user", str(self.user.id))

        res = self.client.get(user_filter_url)

        self.assertContains(res, self.comment)
        self.assertNotContains(res, new_comment)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_list_product_id_filter_successful(self):
        """
        Tests if comment list can be filter by product id
        """
        mock_product = {
            "title": "New Product Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        new_product = Product.objects.create(**mock_product)

        mock_comment = {
            "user": self.user,
            "product": new_product,
            "subject": "New Test comment subject",  # create new comment
            "content": "Test comment content",
            "rate": 4.3,
        }
        new_comment = Comment.objects.create(**mock_comment)  # created new comment

        product_filter_url = get_filter_url("product", str(self.product.id))

        res = self.client.get(product_filter_url)

        self.assertContains(res, self.comment)
        self.assertNotContains(res, new_comment)

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

    def test_comment_detail_patch_public_reject(self):
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

    def test_comment_detail_put_public_reject(self):
        """
        Tests if public user can't put comment detail
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)

        payload = {
            "user": self.user.id,
            "product": self.product.id,
            "subject": "New subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.put(comment_url, payload)
        self.comment.refresh_from_db()

        self.assertNotEqual(self.comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_detail_delete_public_reject(self):
        """
        Tests if public user can't delete comment
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)

        res = self.client.delete(comment_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserCommentAPITest(TestCase):
    """
    Tests private normal user comment api requests
    """

    def setUp(self):
        self.client = APIClient()  # API Client

        main_user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.main_user = get_user_model().objects.create_user(**main_user_data)
        self.client.force_authenticate(user=self.main_user)

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
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

    def test_comment_list_get_normal_user_successful(self):
        """
        Tests if normal user can see comment list
        """
        res = self.client.get(
            COMMENT_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.comment)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_detail_get_normal_user_successful(self):
        """
        Tests if normal user can see comment detail
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)

        res = self.client.get(
            comment_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, comment_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_list_post_normal_user_with_order_successful(self):
        """
        Tests if normal user can create in comment list with order
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",  # create shipping info
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(**mock_shipping_info)

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        Order.objects.create(**mock_order)

        payload = {
            "user": self.main_user.id,
            "product": self.product.id,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(
            COMMENT_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_comment_list_post_to_other_user_with_order_normal_user_reject(self):
        """
        Tests if normal user can't create in comment list with order
        """
        mock_shipping_info = {
            "user": self.user,
            "address": "Test address",  # create shipping info
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(**mock_shipping_info)

        mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        Order.objects.create(**mock_order)

        payload = {
            "user": self.user.id,
            "product": self.product.id,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(
            COMMENT_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_list_post_normal_user_without_order_reject(self):
        """
        Tests if normal user can't create in comment list without order
        """
        payload = {
            "user": self.main_user.id,
            "product": self.product.id,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(
            COMMENT_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_own_comment_detail_patch_normal_reject(self):
        """
        Tests if normal user can't patch his own comment detail
        """
        mock_comment = {
            "user": self.main_user,
            "product": self.product,  # new comment
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        comment = Comment.objects.create(**mock_comment)

        comment_url = get_comment_detail_url([comment])  # get created comment url

        payload = {"subject": "New Subject"}

        res = self.client.patch(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        comment.refresh_from_db()

        self.assertNotEqual(comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_from_other_user_comment_detail_patch_normal_reject(self):
        """
        Tests if normal user can't patch comment detail from other user
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)  # get comment url

        payload = {"subject": "New Subject"}

        res = self.client.patch(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.comment.refresh_from_db()

        self.assertNotEqual(self.comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_comment_detail_put_normal_user_reject(self):
        """
        Tests if normal user can't put own comment detail
        """
        mock_comment = {
            "user": self.main_user,
            "product": self.product,  # new comment
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        comment = Comment.objects.create(**mock_comment)

        comment_url = get_comment_detail_url([comment])  # get created comment url

        payload = {
            "user": self.main_user.id,
            "product": self.product.id,
            "subject": "New subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.put(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        comment.refresh_from_db()

        self.assertNotEqual(comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_from_other_user_comment_detail_put_normal_user_reject(self):
        """
        Tests if normal user can't put comment detail from other user
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)  # get comment url

        payload = {
            "user": self.user.id,
            "product": self.product.id,
            "subject": "New subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.put(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.comment.refresh_from_db()

        self.assertNotEqual(self.comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_comment_detail_delete_normal_user_successful(self):
        """
        Tests if normal user can delete own comment
        """
        mock_comment = {
            "user": self.main_user,
            "product": self.product,  # new comment
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        comment = Comment.objects.create(**mock_comment)

        comment_url = get_comment_detail_url([comment])  # get created comment url

        res = self.client.delete(
            comment_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_from_other_user_comment_detail_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete comment from other user
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)  # get comment url

        res = self.client.delete(
            comment_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperuserCommentAPITest(TestCase):
    """
    Tests private superuser comment api requests
    """

    def setUp(self):
        self.client = APIClient()  # API Client

        main_user_data = {"email": "testmain@test.com", "password": "12345test"}
        self.main_user = get_user_model().objects.create_superuser(**main_user_data)
        self.client.force_authenticate(user=self.main_user)

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",  # Mock product data
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
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

    def test_comment_list_get_superuser_successful(self):
        """
        Tests if superuser can see comment list
        """
        res = self.client.get(
            COMMENT_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.comment)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_detail_get_superuser_successful(self):
        """
        Tests if superuser can see comment detail
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)

        res = self.client.get(
            comment_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, comment_list[0])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_comment_list_post_superuser_with_order_successful(self):
        """
        Tests if superuser can create in comment list with order
        """
        mock_shipping_info = {
            "user": self.main_user,
            "address": "Test address",  # create shipping info
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(**mock_shipping_info)

        mock_order = {
            "buyer": self.main_user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        Order.objects.create(**mock_order)

        payload = {
            "user": self.main_user.id,
            "product": self.product.id,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(
            COMMENT_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_comment_list_post_to_other_user_with_order_superuser_successful(self):
        """
        Tests if superuser can create in comment list with order
        """
        mock_shipping_info = {
            "user": self.user,
            "address": "Test address",  # create shipping info
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        shipping_info = ShippingInfo.objects.create(**mock_shipping_info)

        mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": shipping_info,
        }
        Order.objects.create(**mock_order)

        payload = {
            "user": self.user.id,
            "product": self.product.id,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(
            COMMENT_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_comment_list_post_superuser_without_order_reject(self):
        """
        Tests if superuser can't create in comment list without order
        """
        payload = {
            "user": self.main_user.id,
            "product": self.product.id,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.post(
            COMMENT_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_own_comment_detail_patch_superuser_successful(self):
        """
        Tests if superuser can patch his own comment detail
        """
        mock_comment = {
            "user": self.main_user,
            "product": self.product,  # new comment
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        comment = Comment.objects.create(**mock_comment)

        comment_url = get_comment_detail_url([comment])  # get created comment url

        payload = {"subject": "New Subject"}

        res = self.client.patch(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        comment.refresh_from_db()

        self.assertEqual(comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_from_other_user_comment_detail_patch_superuser_successful(self):
        """
        Tests if superuser can patch comment detail from other user
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)  # get comment url

        payload = {"subject": "New Subject"}

        res = self.client.patch(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.comment.refresh_from_db()

        self.assertEqual(self.comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_own_comment_detail_put_superuser_successful(self):
        """
        Tests if superuser can put own comment detail
        """
        mock_comment = {
            "user": self.main_user,
            "product": self.product,  # new comment
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        comment = Comment.objects.create(**mock_comment)

        comment_url = get_comment_detail_url([comment])  # get created comment url

        payload = {
            "user": self.main_user.id,
            "product": self.product.id,
            "subject": "New subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.put(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        comment.refresh_from_db()

        self.assertEqual(comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_from_other_user_comment_detail_put_superuser_successful(self):
        """
        Tests if superuser can put comment detail from other user
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)  # get comment url

        payload = {
            "user": self.user.id,
            "product": self.product.id,
            "subject": "New subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        res = self.client.put(
            comment_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.comment.refresh_from_db()

        self.assertEqual(self.comment.subject, payload["subject"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_own_comment_detail_delete_superuser_successful(self):
        """
        Tests if superuser can delete own comment
        """
        mock_comment = {
            "user": self.main_user,
            "product": self.product,  # new comment
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }
        comment = Comment.objects.create(**mock_comment)

        comment_url = get_comment_detail_url([comment])  # get created comment url

        res = self.client.delete(
            comment_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_from_other_user_comment_detail_delete_superuser_successful(self):
        """
        Tests if superuser can delete comment from other user
        """
        comment_list = Comment.objects.all()
        comment_url = get_comment_detail_url(comment_list)  # get comment url

        res = self.client.delete(
            comment_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
