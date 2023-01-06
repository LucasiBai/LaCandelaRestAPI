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

    def get_instance(self, request):
        """
        Gets current cart instance and creates one if user don't have cart
        """
        user = get_user_model().objects.filter(id=request.user.id).first()

        cart = self.model.objects.filter(user=user).first()

        if not cart:
            cart = self.model.objects.create(user=user)
            cart.save()

        return cart

    def get(self, request, *args, **kwargs):
        """
        Gets current user cart
        """
        cart = self.get_instance(request)

        serializer = self.serializer_class(cart)

        response = {"data": serializer.data}

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Post cart item into cart
        """
        context = {
            "instance": self.get_instance(request),
            "method": "POST"
        }

        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            response = {"data": serializer.data}
            return Response(response, status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
