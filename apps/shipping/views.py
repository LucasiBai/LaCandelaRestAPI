from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from apps.api_root.utils import FilterMethodsViewset

from .serializers import ShippingInfoSerializer, MyInfoSerializer
from .filters import ShippingInfoFilterset, MyInfoFilterset


class ShippingInfoViewset(FilterMethodsViewset):
    """
    Shipping Info Viewset
    """
    model = ShippingInfoSerializer.Meta.model
    queryset = model.objects.all()

    serializer_class = ShippingInfoSerializer
    my_info_serializer_class = MyInfoSerializer

    filterset_class = ShippingInfoFilterset

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "create" or self.action == "destroy" or self.action == "my_info":
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
                "results": self.get_query_results(),
                "data": ship_info_serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"results": 0, "message": "Not found shipping info."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Creates shipping info view
        """
        context = {
            "user": request.user
        }
        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["get", "post"],
        url_path="my-info",
        filterset_class=MyInfoFilterset
    )
    def my_info(self, request, *args, **kwargs):
        """
        Gets current user shipping info list
        """
        if request.method == "GET":
            user_ship_info = self.filter_queryset(self.get_queryset().filter(user=request.user))

            if user_ship_info:
                serializer = self.serializer_class(user_ship_info, many=True)

                response_data = {
                    "results": self.get_query_results(),
                    "data": serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({"message": "User has not shipping info."}, status=status.HTTP_404_NOT_FOUND)

        elif request.method == "POST":
            context = {
                "user": request.user
            }
            serializer = self.my_info_serializer_class(data=request.data, context=context)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(status=status.HTTP_400_BAD_REQUEST)
