from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.customer_messages.utils.message_sender import MessageSender, EmailSenderStrategy

MESSAGE_SENDERS = {
    "email": EmailSenderStrategy
}


class MessageAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, sender, *args, **kwargs):
        """
        Sends message in selected sender
        """
        if sender not in MESSAGE_SENDERS:
            return Response({"message": "Sender does not exist."}, status=status.HTTP_400_BAD_REQUEST)
