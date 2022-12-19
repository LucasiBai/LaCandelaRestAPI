from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from db.models import Category

CATEGORY_LIST_URL = reverse("api:category-list")


def get_category_detail_url(category_list):
    """
    Gets the category detail url of the first category in list
    """
    return reverse("api:category-detail", kwargs={"pk": category_list[0].id})


class PublicUserCategoryAPITests(TestCase):
    """
    Tests public category api
    """

    def setUp(self):
        self.client = APIClient()

        self.parent_category = Category.objects.create(title="ParentCategory")

        self.child_category = Category.objects.create(
            title="ChildCategory", parent=self.parent_category
        )

    def test_category_list_get_public_successful(self):
        """
        Tests if public user can see the category list
        """

        res = self.client.get(CATEGORY_LIST_URL)

        self.assertContains(res, self.parent_category)

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

    def test_category_detail_get_public_successful(self):
        """
        Tests if public user can see the detail of a category
        """
        category_url = get_category_detail_url([self.parent_category])

        res = self.client.get(category_url)

        self.assertContains(res, self.parent_category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

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
