from django.test import TestCase

from apps.customer_messages.utils.message_sender import MessageSender, EmailSenderStrategy


class MessageSenderTests(TestCase):
    def setUp(self):
        self.context = MessageSender

    def test_context_auto_instance_email_sender_strategy(self):
        """
        Tests if context instance starts with email sender strategy
        """
        context = self.context()

        self.assertEqual(str(context.get_sender()), str(EmailSenderStrategy))
