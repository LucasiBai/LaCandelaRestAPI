from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.users.serializers import UserAccountSerializer

from db.models import Cart

from .utils.payment_methods import PaymentMethod, MercadoPagoMethod
from .utils.order_creation import OrderCreation

PAYMENT_METHODS = {
    "mp": MercadoPagoMethod
}

ORDER_CREATORS = {
    "mp": OrderCreation
}


class CheckoutAPIView(APIView):
    """
    Checkout APIView
    """

    def get(self, request, method, cart_id, *args, **kwargs):
        """
        Gets checkout of selected payment method
        """
        cart = Cart.objects.filter(id=cart_id).first()

        if cart and method.lower() in PAYMENT_METHODS:
            if cart.user.id != request.user.id:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            pay_method = PAYMENT_METHODS[method.lower()]
            payment = PaymentMethod(cart=cart, method=pay_method)

            user_serializer = UserAccountSerializer(cart.user)

            export_data = {
                "user": user_serializer.data,
                "preference": payment.get_preference()
            }

            return Response(export_data, status=status.HTTP_200_OK)

        return Response({"message": f"{'cart id' if not cart else 'method'} is invalid."},
                        status=status.HTTP_400_BAD_REQUEST)


class CheckoutNotificationAPIView(APIView):
    """
    Checkout Notification APIView
    """

    permission_classes = [AllowAny]

    def post(self, request, method, *args, **kwargs):
        """
        Create Order if product pay was success
        """
        if method.lower() in ORDER_CREATORS:
            order_creator_method = ORDER_CREATORS[method.lower()]

            order_creator = order_creator_method()

            return order_creator.get_response(request.data)

        return Response({"message": "method is invalid."}, status=status.HTTP_400_BAD_REQUEST)
