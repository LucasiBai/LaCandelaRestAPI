from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.users.serializers import UserAccountSerializer

from db.models import Cart

from .utils import PaymentMethod, MercadoPagoMethod

PAYMENT_METHODS = {
    "mp": MercadoPagoMethod
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

        if cart and method in PAYMENT_METHODS:
            if cart.user.id != request.user.id:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            pay_method = PAYMENT_METHODS[method]
            payment = PaymentMethod(cart=cart, state=pay_method)

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

    def post(self, request, *args, **kwargs):
        """
        Create Order if product pay was success
        """
        return Response(request.data, status=status.HTTP_200_OK)
