from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CartSerializer, CartItemSerializer


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


class CartItemRetrieveApiView(APIView):
    """
    Cart Item Retrieve Apiview
    """

    model = CartItemSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = CartItemSerializer

    def delete(self, request, pk, *args, **kwargs):
        """
        Deletes selected Cart Item
        """
        cart_item = self.queryset.filter(pk=pk).first()

        if cart_item:
            cart = cart_item.cart

            if not request.user.id == cart.user.id:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            cart.remove_product(cart_item.product)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "Cart Item not found."}, status=status.HTTP_404_NOT_FOUND)
