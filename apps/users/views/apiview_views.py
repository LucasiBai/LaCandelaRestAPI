from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.users.serializers import (
    ResetPasswordSerializer,
    ChangePasswordConfirmSerializer,
)


class ResetPasswordApiView(APIView):
    """
    Api view for forgotten password
    """

    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Email sended"}, status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordConfirmApiView(APIView):
    """
    Changes the password if params are valid
    """

    serializer_class = ChangePasswordConfirmSerializer
    permission_classes = [AllowAny]

    def patch(self, request, *args, **kwargs):
        context = {"token": kwargs["token"], "encoded_pk": kwargs["encoded_pk"]}

        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
