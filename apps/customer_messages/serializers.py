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
        sender.send_message(self.validated_data)
