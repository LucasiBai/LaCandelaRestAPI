from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CartSerializer


class CartApiView(APIView):
    """
    Cart Apiview
    """

    model = CartSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = CartSerializer

    def get(self, request, *args, **kwargs):
        """
        Gets current user cart
        """
        user = get_user_model().objects.filter(id=request.user.id).first()

        cart = self.model.objects.filter(user=user).first()

        if not cart:
            cart = self.model.objects.create(user=user)
            cart.save()

        serializer = self.serializer_class(cart)

        response = {"data": serializer.data}

        return Response(response, status=status.HTTP_200_OK)
