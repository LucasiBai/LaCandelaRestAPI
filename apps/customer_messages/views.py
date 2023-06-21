from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.customer_messages.serializers import MessageSerializer
from apps.customer_messages.utils.message_sender import MessageSender, EmailSenderStrategy

MESSAGE_SENDERS = {
    "email": EmailSenderStrategy
}


class MessageAPIView(APIView):
    """
    Message APIView
    """
    serializer_class = MessageSerializer

    permission_classes = [AllowAny]

    def post(self, request, sender, *args, **kwargs):
        """
        Sends message in selected sender
        """
        sender_method = sender.lower()

        if sender_method not in MESSAGE_SENDERS:
            return Response({"message": "Sender does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        selected_sender = MESSAGE_SENDERS[sender_method]

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=MessageSender(selected_sender))
            return Response({"message": "Message sent successful."}, status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
