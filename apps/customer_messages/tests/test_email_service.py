from django.test import TestCase

from apps.customer_messages.utils.services.email_service import EmailService


class EmailServiceTests(TestCase):
    """
    Tests Email Service
    """

    def setUp(self):
        self.service = EmailService

    def test_service_send_email_method_successful(self):
        """
        Tests if service can send email correctly
        """
        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "email_from": "testemail@test.com",
            "recipient_email": "recipientemail@test.com"
        }

        self.assertTrue(self.service.send_email_to(**payload))

    def test_service_send_email_no_param_reject(self):
        """
        Tests if service raise an error when don't have required param
        """
        payload = {
            "message": "Test Message",
            "email_from": "testemail@test.com",
            "recipient_email": "recipientemail@test.com"
        }

        with self.assertRaises(ValueError):
            self.service.send_email_to(**payload)

        payload = {
            "subject": "Test Subject",
            "email_from": "testemail@test.com",
            "recipient_email": "recipientemail@test.com"
        }

        with self.assertRaises(ValueError):
            self.service.send_email_to(**payload)

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "recipient_email": "recipientemail@test.com"
        }

        with self.assertRaises(ValueError):
            self.service.send_email_to(**payload)

        payload = {
            "subject": "Test Subject",
            "message": "Test Message",
            "email_from": "testemail@test.com",
        }

        with self.assertRaises(ValueError):
            self.service.send_email_to(**payload)
