from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from db.models import Category

CATEGORY_LIST_URL = reverse("api:category-list")  # category token api url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url


def get_category_detail_url(category_list):
    """
    Gets the category detail url of the first category in list
    """
    return reverse("api:category-detail", kwargs={"pk": category_list[0].id})


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return CATEGORY_LIST_URL + f"?{filter_name}={value}"


class PublicUserCategoryAPITests(TestCase):
    """
    Tests public category api
    """

    def setUp(self):
        self.client = APIClient()

        self.model = Category

        self.parent_category = self.model.objects.create(title="ParentCategory")

        self.child_category = self.model.objects.create(
            title="ChildCategory", parent=self.parent_category
        )

    def test_category_list_get_public_successful(self):
        """
        Tests if public user can see the category list
        """

        res = self.client.get(CATEGORY_LIST_URL)

        self.assertContains(res, self.parent_category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_list_render_sub_categories_get_public_successful(self):
        """
        Tests if public user can see the category list
        """

        res = self.client.get(CATEGORY_LIST_URL)

        self.assertContains(res, self.parent_category)
        self.assertContains(res, self.child_category)

        self.assertEqual(
            res.data[0]["subcategories"][0]["id"],  # parent child children
            self.child_category.id,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_list_get_limit_filter_successful(self):
        """
        Tests if can filter category list with limit
        """
        first_parent_category = self.model.objects.create(title="First Parent Category")
        second_parent_category = self.model.objects.create(
            title="Second Parent Category"
        )

        limit_filter_url = get_filter_url("limit", "2")

        res = self.client.get(limit_filter_url)

        self.assertContains(res, self.parent_category)
        self.assertContains(res, first_parent_category)
        self.assertNotContains(res, second_parent_category)

    def test_category_list_get_offset_filter_successful(self):
        """
        Tests if can filter category list with offset
        """
        first_parent_category = self.model.objects.create(title="First Parent Category")
        second_parent_category = self.model.objects.create(
            title="Second Parent Category"
        )

        offset_filter_url = get_filter_url("offset", "2")

        res = self.client.get(offset_filter_url)

        self.assertNotContains(res, self.parent_category)
        self.assertContains(res, first_parent_category)
        self.assertContains(res, second_parent_category)

    def test_category_list_get_title_no_case_sensitive_filter_successful(self):
        """
        Tests if can filter category list with title
        """
        first_parent_category = self.model.objects.create(title="First Parent Category")
        second_parent_category = self.model.objects.create(
            title="Second Parent Category"
        )

        title_filter_url = get_filter_url("parent_title", "parent cat")

        res = self.client.get(title_filter_url)

        self.assertNotContains(res, self.parent_category)
        self.assertContains(res, first_parent_category)
        self.assertContains(res, second_parent_category)

    def test_parent_category_detail_get_public_successful(self):
        """
        Tests if public user can see the detail of parent category
        """
        category_url = get_category_detail_url([self.parent_category])

        res = self.client.get(category_url)

        self.assertContains(res, self.parent_category)
        self.assertContains(res, "subcategories")
        self.assertNotContains(res, "parent")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_child_category_detail_get_public_successful(self):
        """
        Tests if public user can see the detail of child category
        """
        category_url = get_category_detail_url([self.child_category])

        res = self.client.get(category_url)

        self.assertContains(res, self.child_category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_list_post_public_reject(self):
        """
        Tests if public user can't post into category list
        """
        payload = {
            "title": "Test Post Category",
        }

        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_detail_partial_update_public_reject(self):
        """
        Tests if public user can't partial update a category
        """
        category_url = get_category_detail_url([self.parent_category])

        payload = {
            "title": "New Test Title",  # Mock update category
        }

        res = self.client.patch(category_url, payload)
        self.parent_category.refresh_from_db()

        self.assertNotEqual(self.parent_category.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_detail_update_public_reject(self):
        """
        Tests if public user can't update a category
        """
        category_url = get_category_detail_url([self.parent_category])

        payload = {"title": "New Test Title"}

        res = self.client.put(category_url, payload)
        self.parent_category.refresh_from_db()

        self.assertNotEqual(self.parent_category.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_detail_delete_public_reject(self):
        """
        Tests if public user can't delete a category
        """

        category_url = get_category_detail_url([self.parent_category])

        res = self.client.delete(category_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserCategoryAPITests(TestCase):
    """
    Tests private normal user category api
    """

    def setUp(self):
        self.client = APIClient()

        self.model = Category

        main_user_data = {
            "email": "normaluser@test.com",  # create user data
            "password": "testPassword",
        }
        self.main_user = get_user_model().objects.create_user(
            **main_user_data  # create normal user
        )

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.parent_category = self.model.objects.create(title="ParentCategory")

        self.child_category = self.model.objects.create(
            title="ChildCategory", parent=self.parent_category
        )

    def test_category_list_get_normal_user_successful(self):
        """
        Tests if normal user can see the category list
        """

        res = self.client.get(
            CATEGORY_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.parent_category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_list_post_normal_user_reject(self):
        """
        Tests if normal user can't post into category list
        """
        payload = {
            "title": "Test Post Category",
        }

        res = self.client.post(
            CATEGORY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail_get_normal_user_successful(self):
        """
        Tests if normal user can see the detail of a category
        """
        category_url = get_category_detail_url([self.parent_category])

        res = self.client.get(
            category_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.parent_category)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

    def test_category_detail_partial_update_normal_user_reject(self):
        """
        Tests if normal user can't partial update a category
        """
        category_url = get_category_detail_url([self.parent_category])

        payload = {
            "title": "New Test Title",  # Mock update category
        }

        res = self.client.patch(
            category_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.parent_category.refresh_from_db()

        self.assertNotEqual(self.parent_category.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail_update_normal_user_reject(self):
        """
        Tests if normal user can't update a category
        """
        category_url = get_category_detail_url([self.parent_category])

        payload = {"title": "New Test Title"}

        res = self.client.put(
            category_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.parent_category.refresh_from_db()

        self.assertNotEqual(self.parent_category.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail_delete_normal_user_reject(self):
        """
        Tests if normal user can't delete a category
        """

        category_url = get_category_detail_url([self.parent_category])

        res = self.client.delete(
            category_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperuserCategoryAPITests(TestCase):
    """
    Tests private superuser category api
    """

    def setUp(self):
        self.client = APIClient()

        self.model = Category

        main_user_data = {
            "email": "normaluser@test.com",  # create user data
            "password": "testPassword",
        }
        self.main_user = get_user_model().objects.create_superuser(
            **main_user_data  # create normal user
        )

        res_token = self.client.post(TOKEN_URL, main_user_data)  # get user token
        self.user_token = res_token.data["token"]

        self.parent_category = self.model.objects.create(title="ParentCategory")

        self.child_category = self.model.objects.create(
            title="ChildCategory", parent=self.parent_category
        )

    def test_category_list_get_superuser_successful(self):
        """
        Tests if superuser can see the category list
        """

        res = self.client.get(
            CATEGORY_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.parent_category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_list_post_parent_superuser_successful(self):
        """
        Tests if superuser can post into category list a parent
        """
        payload = {
            "title": "Test Post Category",
        }

        res = self.client.post(
            CATEGORY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_category_list_post_child_superuser_successful(self):
        """
        Tests if superuser can post into category list a child
        """
        mock_parent_category = {
            "title": "Test Parent Category",
        }
        parent_category = self.model.objects.create(**mock_parent_category)

        payload = {
            "title": "Test Child Category",
            "parent": parent_category.id,
        }

        res = self.client.post(
            CATEGORY_LIST_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_category_detail_get_superuser_successful(self):
        """
        Tests if superuser can see the detail of a category
        """
        category_url = get_category_detail_url([self.parent_category])

        res = self.client.get(
            category_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertContains(res, self.parent_category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_detail_partial_update_superuser_successful(self):
        """
        Tests if superuser can partial update a category
        """
        category_url = get_category_detail_url([self.parent_category])

        payload = {
            "title": "New Test Title",  # Mock update category
        }

        res = self.client.patch(
            category_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.parent_category.refresh_from_db()

        self.assertEqual(self.parent_category.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_detail_update_superuser_successful(self):
        """
        Tests if superuser can update a category
        """
        category_url = get_category_detail_url([self.parent_category])

        payload = {"title": "New Test Title"}

        res = self.client.put(
            category_url, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.parent_category.refresh_from_db()

        self.assertEqual(self.parent_category.title, payload["title"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_detail_delete_superuser_successful(self):
        """
        Tests if superuser can delete a category
        """

        category_url = get_category_detail_url([self.parent_category])

        res = self.client.delete(
            category_url, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
