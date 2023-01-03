from rest_framework.views import APIView

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
