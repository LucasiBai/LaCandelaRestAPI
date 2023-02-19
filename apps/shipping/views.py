from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import ShippingInfoSerializer


class ShippingInfoViewset(ModelViewSet):
    """
    Shipping Info Viewset
    """
    model = ShippingInfoSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = ShippingInfoSerializer

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "create" or self.action == "destroy":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        Returns Shipping info destroy reject response
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        """
        Gets shipping info list with result quantity
        """
        ship_info_list = self.filter_queryset(self.get_queryset())

        if ship_info_list:
            ship_info_serializer = self.serializer_class(ship_info_list, many=True)

            response_data = {
                "results": len(ship_info_serializer.data),
                "data": ship_info_serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"results": 0, "message": "Not found shipping info."}, status=status.HTTP_404_NOT_FOUND)
