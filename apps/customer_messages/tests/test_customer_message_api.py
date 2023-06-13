from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.customer_messages.utils.message_sender import MessageSender, EmailSenderStrategy


class MessageAPIViewsetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_message_api_email_post_customer_message_successful(self):
        """
        Tests if message api send an email with post data
        """
