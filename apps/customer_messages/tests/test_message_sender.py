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


class MockBadTypeSender:
    """
    Mock Bad Type of Sender Strategy
    """


class MessageSenderTests(TestCase):
    def setUp(self):
        self.context = MessageSender

        self.mock_sender = MockSenderStrategy

    # Context Tests
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

    def test_context_change_sender_method_successful(self):
        """
        Tests if context method can update current sender
        """
        context = self.context(EmailSenderStrategy)
        self.assertEqual(str(context.get_sender()), str(EmailSenderStrategy()))

        context.change_sender(MockSenderStrategy)
        self.assertEqual(str(context.get_sender()), str(MockSenderStrategy()))

    def test_context_change_sender_method_no_param_reject(self):
        """
        Tests if method raise an error with no param entered
        """
        context = self.context(EmailSenderStrategy)

        with self.assertRaises(ValueError):
            context.change_sender()

    # Email Sender Tests
    def test_email_sender_send_message_params_successful(self):
        """
        Tests if email sender runs correctly when pass correct data type in send_message method
        """
        context = self.context(EmailSenderStrategy)

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com",
            "recipient_email": "testrecipient@test.com"
        }

        self.assertTrue(context.send_message(**payload))

    def test_email_sender_send_message_subject_incorrect_param_type_reject(self):
        """
        Tests if sender raise an error with incorrect param type in send_message method
        """

        context = self.context(EmailSenderStrategy)

        payload = {
            "subject": 0,
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com",
            "recipient_email": "testrecipient@test.com"
        }

        with self.assertRaises(ValueError):
            context.send_message(**payload)

    def test_email_sender_send_message_message_incorrect_param_type_reject(self):
        """
        Tests if sender raise an error with incorrect param type in send_message method
        """

        context = self.context(EmailSenderStrategy)

        payload = {
            "subject": "Test Subject",
            "message": 0,
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com",
            "recipient_email": "testrecipient@test.com"
        }

        with self.assertRaises(ValueError):
            context.send_message(**payload)

    def test_email_sender_send_message_full_name_from_incorrect_param_type_reject(self):
        """
        Tests if sender raise an error with incorrect param type in send_message method
        """

        context = self.context(EmailSenderStrategy)

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": 0,
            "email_from": "testemail@test.com",
            "recipient_email": "testrecipient@test.com"
        }

        with self.assertRaises(ValueError):
            context.send_message(**payload)

    def test_email_sender_send_message_email_from_incorrect_param_type_reject(self):
        """
        Tests if sender raise an error with incorrect param type in send_message method
        """

        context = self.context(EmailSenderStrategy)

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": 0,
            "recipient_email": "testrecipient@test.com"
        }

        with self.assertRaises(ValueError):
            context.send_message(**payload)

    def test_email_sender_send_message_recipient_email_incorrect_param_type_reject(self):
        """
        Tests if sender raise an error with incorrect param type in send_message method
        """

        context = self.context(EmailSenderStrategy)

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "full_name_from": "Test Name",
            "email_from": "testemail@test.com",
            "recipient_email": 0
        }

        with self.assertRaises(ValueError):
            context.send_message(**payload)
