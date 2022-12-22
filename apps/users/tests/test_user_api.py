from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from rest_framework_simplejwt.exceptions import TokenError

from apps.users.utils import get_reset_password_url

USER_LIST_URL = reverse("users:user_account-list")  # user list API url
ME_URL = reverse("users:user_account-get-me-data")  # get user API url
RESET_PASSWORD_URL = reverse("users:reset_password")  # get user reset password API url

TOKEN_URL = reverse("users:user_token_obtain")  # user token API url
TOKEN_REFRESH_URL = reverse("users:user_token_refresh")  # user token refresh API url


def get_change_password_url(token, encoded_pk):
    """
    Gets the change password url with params
    """
    return reverse(
        "users:reset_password-confirm",
        kwargs={"token": token, "encoded_pk": encoded_pk},
    )


def create_user(**kwargs):
    """
    Function to create an user in db
    """
    return get_user_model().objects.create_user(**kwargs)


def get_filter_url(filter_name, value):
    """
    Gets the filter url
    """
    return USER_LIST_URL + f"?{filter_name}={value}"


class PublicUsersAPITests(TestCase):
    """
    Tests public users api
    """

    def setUp(self):
        """
        Set up Public user api
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Tests if it is possible to create a user with email address in API
        """
        payload = {
            "email": "test@mitest.com",
            "password": "testpassword",  # Mock user create data
            "first_name": "Test",
            "last_name": "Testi",
        }

        res = self.client.post(USER_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """
        Tests if exists the inserted user
        """
        payload = {
            "email": "test@mitest.com",
            "password": "testpassword",  # Mock user create data
            "first_name": "Test",
        }
        create_user(**payload)

        res = self.client.post(USER_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_invalid_email(self):
        """
        Tests if catch exception of invalid email adress
        """
        payload = {
            "email": "test@.com",
            "password": "testpassword",  # Mock user create data
            "first_name": "Test",
        }

        res = self.client.post(USER_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_user_password_too_short(self):
        """
        Tests if catch exception of short password
        """
        payload = {
            "email": "test@test.com",
            "password": "123",  # Mock user create data
            "first_name": "Test",
        }

        res = self.client.post(USER_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_unauthorized_user_view_user_data_list_reject(self):
        """
        Tests if unauthorized user can't see user list
        """
        res = self.client.get(USER_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_for_user(self):
        """
        Tests if can create JWT succesfuly
        """
        payload = {
            "email": "test@.com",
            "password": "testpassword",  # Mock user create data
            "first_name": "Test",
        }

        user = create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertIn("refresh-token", res.data)
        self.assertIn("message", res.data)

        self.assertEqual(user.email, res.data["user"]["email"])

        self.assertEqual(status.HTTP_202_ACCEPTED, res.status_code)

    def test_create_token_invalid_credentials(self):
        """
        Tests if JWT was'nt created without invalid credentials
        """

        create_user(email="test@test.com", password="test123")

        payload = {
            "email": "test@test.com",
            "password": "wrongpassword",  # Mock wrong user password data
            "first_name": "Test",
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Tests if JWT was'nt created without user
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Tests if email and password are required
        """
        res = self.client.post(TOKEN_URL, {"email": "", "password": ""})

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_success(self):
        """
        Tests if can refresh the JWT
        """
        payload = {
            "email": "test@test.com",
            "password": "testpassword",  # Mock user create data
            "first_name": "Test",
        }
        create_user(**payload)

        res_token = self.client.post(TOKEN_URL, payload)
        refresh_token = res_token.data["refresh-token"]

        res_refresh = self.client.post(
            TOKEN_REFRESH_URL, {"refresh-token": refresh_token}
        )

        self.assertIn("updated-token", res_refresh.data)
        self.assertIn("message", res_refresh.data)

        self.assertEqual(res_refresh.status_code, status.HTTP_202_ACCEPTED)

    def test_invalid_refresh_token(self):
        """
        Tests if refresh token raise exception
        """

        with self.assertRaises(TokenError):
            self.client.post(
                TOKEN_REFRESH_URL,
                {"refresh-token": "invalid.token.id"},
            )

    def test_retrieve_user_unauthorized(self):
        """
        Tests if rejects the unauthorized data
        """

        res = self.client.get(ME_URL)

        self.assertNotIn("email", res.data)
        self.assertNotIn("username", res.data)
        self.assertNotIn("first_name", res.data)
        self.assertNotIn("last_name", res.data)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_forgotten_password_successful(self):
        """
        Tests if can send email to change forgotten password
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }
        create_user(**payload)

        res = self.client.post(RESET_PASSWORD_URL, {"email": payload["email"]})

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

    def test_user_forgotten_password_invalid_email(self):
        """
        Tests if invalid email returns 404
        """

        res = self.client.post(RESET_PASSWORD_URL, {"email": "invalidEmail@test.com"})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_reset_password_url_successful(self):
        """
        Tests if generated reset password url is valid
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }
        user = create_user(**payload)

        reset_url_params = get_reset_password_url(payload["email"]).split("/")

        token = reset_url_params[-2]
        encoded_pk = reset_url_params[-3]

        self.assertTrue(PasswordResetTokenGenerator().check_token(user, token))
        self.assertEqual(urlsafe_base64_decode(encoded_pk).decode(), str(user.id))

    def test_change_password_api_successful(self):
        """
        Tests if public user can change the password successfuly
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }
        user = create_user(**payload)

        reset_url_params = get_reset_password_url(payload["email"]).split("/")

        token = reset_url_params[-2]
        encoded_pk = reset_url_params[-3]

        CHANGE_PASSWORD_URL = get_change_password_url(token, encoded_pk)

        res = self.client.patch(CHANGE_PASSWORD_URL, {"password": "NewPassword"})

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPassword"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_api_invalid_token_reject(self):
        """
        Tests if public user can change the password successfuly
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }
        user = create_user(**payload)

        reset_url_params = get_reset_password_url(payload["email"]).split("/")

        token = "invalidToken123"
        encoded_pk = reset_url_params[-3]

        CHANGE_PASSWORD_URL = get_change_password_url(token, encoded_pk)

        res = self.client.patch(CHANGE_PASSWORD_URL, {"password": "NewPassword"})

        user.refresh_from_db()
        self.assertFalse(user.check_password("NewPassword"))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_api_invalid_pk_reject(self):
        """
        Tests if public user can change the password successfuly
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }
        user = create_user(**payload)

        reset_url_params = get_reset_password_url(payload["email"]).split("/")

        token = reset_url_params[-2]
        encoded_pk = "NDEyMTQzNjEyNDUyNDM="

        CHANGE_PASSWORD_URL = get_change_password_url(token, encoded_pk)

        res = self.client.patch(CHANGE_PASSWORD_URL, {"password": "NewPassword"})

        user.refresh_from_db()
        self.assertFalse(user.check_password("NewPassword"))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_api_invalid_data_reject(self):
        """
        Tests if public user cannot change the password with invalid data
        """
        payload = {
            "email": "test@test.com",
            "password": "Test123",  # Mock user data
            "first_name": "Test",
        }
        user = create_user(**payload)

        token = "invalidToken123"
        encoded_pk = "NDEyMTQzNjEyNDUyNDM="

        CHANGE_PASSWORD_URL = get_change_password_url(token, encoded_pk)

        res = self.client.patch(CHANGE_PASSWORD_URL, {"password": "NewPassword"})

        user.refresh_from_db()
        self.assertFalse(user.check_password("NewPassword"))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_user_put_another_user_data_reject(self):
        """
        Tests if public user can't put another user data
        """
        new_data_payload = {
            "email": "newemail@test.com",
            "password": "passwordUpdated",
            "first_name": "New Name",
            "last_name": "New Last Name",
            "is_active": True,
            "is_staff": True,
        }

        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}
        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.put(
            USER_DETAIL_URL,
            new_data_payload,
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersAPITests(TestCase):
    """
    Tests private users api
    """

    def setUp(self):
        self.client = APIClient()

        self.user_data = {"email": "test@test.com", "password": "test123"}

        self.user = create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

        res_token = self.client.post(TOKEN_URL, self.user_data)  # get user token
        self.user_token = res_token.data["token"]

    def test_retrieve_user_success(self):
        """
        Tests gets the user data
        """

        res = self.client.get(ME_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["first_name"], self.user.first_name)

        self.assertNotIn("password", res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_me_not_allowed(self):
        """
        Tests if posts is not allowed
        """
        res = self.client.post(
            ME_URL,
            {"email": "test@email.com", "password": "test123"},
        )

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_data_successful(self):
        """
        Tests if authorized user can update profile
        """
        payload = {
            "email": "newemail@test.com",
            "password": "newpassword",  # Mock user data
            "first_name": "NewName",
            "last_name": "NewLast",
        }

        res = self.client.patch(
            ME_URL, payload, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )
        self.user.refresh_from_db()

        self.assertEqual(res.data["email"], payload["email"])
        self.assertEqual(res.data["first_name"], payload["first_name"])
        self.assertTrue(self.user.check_password(payload["password"]))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_normal_user_view_user_data_list_reject(self):
        """
        Tests if normal user can't see user list
        """
        res = self.client.get(
            USER_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_view_another_user_data_reject(self):
        """
        Tests if normal user can't see another user data
        """
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}
        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.get(
            USER_DETAIL_URL, HTTP_AUTHORIZATION=f"Bearer {self.user_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_patch_another_user_data_reject(self):
        """
        Tests if normal user can't patch another user data
        """
        new_data_payload = {"email": "newemail@test.com"}
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}

        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.patch(
            USER_DETAIL_URL,
            new_data_payload,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_put_another_user_data_reject(self):
        """
        Tests if normal user can't put another user data
        """
        new_data_payload = {
            "email": "newemail@test.com",
            "password": "passwordUpdated",
            "first_name": "New Name",
            "last_name": "New Last Name",
            "is_active": True,
            "is_staff": True,
        }
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}

        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.put(
            USER_DETAIL_URL,
            new_data_payload,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_delete_another_user_data_reject(self):
        """
        Tests if normal user can't delete another user data
        """
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}

        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.delete(
            USER_DETAIL_URL,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperusersAPITests(TestCase):
    """
    Tests private users api
    """

    def setUp(self):
        self.client = APIClient()

        self.user_data = {"email": "test@test.com", "password": "test123"}

        self.superuser = get_user_model().objects.create_superuser(**self.user_data)
        self.client.force_authenticate(user=self.superuser)

        res_token = self.client.post(TOKEN_URL, self.user_data)  # get user token
        self.superuser_token = res_token.data["token"]

    def test_superuser_view_user_data_list_successful(self):
        """
        Tests if superuser can see user list
        """
        res = self.client.get(
            USER_LIST_URL, HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_superuser_view_user_data_list_offset_filter_successful(self):
        """
        Tests if superuser can see user list with offset filter
        """
        first_user_created = create_user(email="testfirst@test.com")
        second_user_created = create_user(email="testsecond@test.com")

        offset_filter_url = get_filter_url("offset", "2")

        res = self.client.get(
            offset_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}"
        )

        self.assertNotContains(res, self.superuser)
        self.assertContains(res, first_user_created)
        self.assertContains(res, second_user_created)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_superuser_view_user_data_list_limit_filter_successful(self):
        """
        Tests if superuser can see user list with limit filter
        """
        first_user_created = create_user(email="testfirst@test.com")
        second_user_created = create_user(email="testsecond@test.com")

        limit_filter_url = get_filter_url("limit", "2")

        res = self.client.get(
            limit_filter_url, HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}"
        )

        self.assertContains(res, self.superuser)
        self.assertContains(res, first_user_created)
        self.assertNotContains(res, second_user_created)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_superuser_view_another_user_data_successful(self):
        """
        Tests if superuser can see another user data
        """
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}
        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.get(
            USER_DETAIL_URL, HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_superuser_patch_another_user_data_successful(self):
        """
        Tests if superuser can patch another user data
        """
        new_data_payload = {"email": "newemail@test.com"}
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}

        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.patch(
            USER_DETAIL_URL,
            new_data_payload,
            HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_superuser_put_another_user_data_successful(self):
        """
        Tests if superuser can put another user data
        """
        new_data_payload = {
            "email": "newemail@test.com",
            "password": "passwordUpdated",
            "first_name": "New Name",
            "last_name": "New Last Name",
            "is_active": True,
            "is_staff": True,
        }

        new_user_payload = {
            "email": "newuser@test.com",  # New User
            "password": "newuserpassword",
        }
        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.put(
            USER_DETAIL_URL,
            new_data_payload,
            HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_superuser_delete_another_user_data_successful(self):
        """
        Tests if superuser can delete another user data
        """
        new_user_payload = {"email": "newuser@test.com", "password": "newuserpassword"}

        user = get_user_model().objects.create_user(**new_user_payload)

        USER_DETAIL_URL = reverse("users:user_account-detail", kwargs={"pk": user.id})

        res = self.client.delete(
            USER_DETAIL_URL,
            HTTP_AUTHORIZATION=f"Bearer {self.superuser_token}",
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
