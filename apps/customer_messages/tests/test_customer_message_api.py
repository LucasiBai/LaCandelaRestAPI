from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from apps.customer_messages.utils.message_sender import MessageSender, EmailSenderStrategy


def get_message_sender_url(sender: str):
    """
    Gets message sender api url with entered sender type

    Args:
        sender(SenderStrategyInterface): sender selected

    Returns:
        Message sender url
    """
    return reverse("api:message", kwargs={"sender": sender})


class MessageAPIViewsetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.senders_tag = {
            "email": "email"
        }

    def test_message_api_email_get_method_not_allowed_reject(self):
        """
        Tests if api do not allowed get method
        """
        email_sender_url = get_message_sender_url(self.senders_tag["email"])

        res = self.client.get(email_sender_url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_message_api_email_post_customer_message_successful(self):
        """
        Tests if message api send an email with post data
        """
        email_sender_url = get_message_sender_url(self.senders_tag["email"])

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com"
        }

        res = self.client.post(email_sender_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["message"], "Message sent successful.")

    def test_message_api_email_post_customer_message_no_case_sensitive_successful(self):
        """
        Tests if message api send an email with post data, no case-sensitive url
        """
        email_sender_url = get_message_sender_url(self.senders_tag["email"].upper())

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com"
        }

        res = self.client.post(email_sender_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["message"], "Message sent successful.")

    def test_message_api_no_existent_sender_reject(self):
        """
        Tests if message api can raise an error with no existent sender
        """
        email_sender_url = get_message_sender_url("no-existent-sender")

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com"
        }

        res = self.client.post(email_sender_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertContains(res.data, "Sender does not exist.")
