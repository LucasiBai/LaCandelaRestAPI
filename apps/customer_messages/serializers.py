from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    """
    Message Serializer
    """
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
    full_name_from = serializers.CharField(max_length=255)
    email_from = serializers.EmailField()

    def save(self, **kwargs):
        sender = kwargs.get("sender", None)

        subject = self.validated_data.get("subject")
        message = self.validated_data.get("message")
        full_name_from = self.validated_data.get("full_name_from")
        email_from = self.validated_data.get("email_from")

        sender.send_message(subject=subject, message=message, full_name_from=full_name_from, email_from=email_from,
                            recipient_email="")
