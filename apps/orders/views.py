from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from apps.api_root.utils import FilterMethodsViewset
from .serializers import OrderSerializer
from .filters import OrderFilterset


class OrderViewset(FilterMethodsViewset):
    """
    Order API Viewset
    """

    model = OrderSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilterset

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "get_mine_orders":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Gets orders and results quantity
        """
        orders = self.filter_queryset(self.get_queryset())

        if orders:
            serializer = self.serializer_class(orders, many=True)

            export_data = {
                "results": self.results,
                "data": serializer.data,
            }

            return Response(export_data, status=status.HTTP_200_OK)

        return Response(
            {"results": 0, "message": "Not found orders."},
            status=status.HTTP_204_NO_CONTENT,
        )

    def create(self, request, *args, **kwargs):
        """
        Custom create view
        """
        context = {"user": request.user, "action": "create"}
        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["get", "post"],
        url_path="mine",
    )
    def get_mine_orders(self, request, *args, **kwargs):
        """
        Custom action view with orders of current user
        """

        user_orders = self.filter_queryset(
            self.get_queryset().filter(buyer=request.user)
        )

        if request.method == "GET":
            if user_orders:
                serializer = self.serializer_class(user_orders, many=True)

                export_data = {
                    "results": self.get_query_results(),
                    "data": serializer.data,
                }

                return Response(export_data, status=status.HTTP_200_OK)
            return Response(
                {"results": 0, "message": "User have not placed orders yet"},
                status.HTTP_204_NO_CONTENT,
            )

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
