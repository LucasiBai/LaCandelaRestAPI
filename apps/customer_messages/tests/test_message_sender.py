from django.test import TestCase

from apps.customer_messages.utils.models.sender_strategy import SenderStrategyInterface
from apps.customer_messages.utils.message_sender import MessageSender, EmailSenderStrategy


class MockSenderStrategy(SenderStrategyInterface):
    """
    Mock Sender Strategy
    """

    def __str__(self):
        return "Mock Sender"

    def send_message(self, subject=None, message=None, full_name_from: str = None, email_from=None,
                     recipient_email=None):
        print(subject, message, email_from, recipient_email)
        return self.get_message_template(message)

    @staticmethod
    def get_message_template(message: str):
        """
        Returns message template
        """
        return f"'{message}' sent with mock sender"


class MessageSenderTests(TestCase):
    def setUp(self):
        self.context = MessageSender

        self.mock_sender = MockSenderStrategy

    def test_context_auto_instance_email_sender_strategy_successful(self):
        """
        Tests if context instance starts with email sender strategy
        """
        context = self.context()

        self.assertEqual(str(context.get_sender()), str(EmailSenderStrategy()))

    def test_context_send_message_successful(self):
        """
        Tests if context can init sender
        """
        context = self.context(self.mock_sender)

        self.assertEqual(self.mock_sender.get_message_template("Test Message"),
                         context.send_message(message="Test Message"))
