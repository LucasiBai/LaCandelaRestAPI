from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .filters import ProductsFilterSet
from apps.products.serializers import ProductSerializer


class ProductsViewSet(ModelViewSet):
    """
    Products model viewset
    """

    model = ProductSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductsFilterSet

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def filter_queryset(self, queryset):
        """
        Gets the filtered queryset and total results from filterset
        """
        for backend in list(self.filter_backends):
            backend_data = backend().filter_queryset(self.request, queryset, self)

            queryset = backend_data["queryset"]

            self.results = backend_data["results"]
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Gets products and results quantity
        """
        products = self.filter_queryset(self.get_queryset())

        if products:
            serializer = self.serializer_class(products, many=True)

            export_data = {"results": self.results, "data": serializer.data}

            return Response(export_data, status=status.HTTP_200_OK)

        return Response(
            {"results": 0, "message": "Not found products."},
            status=status.HTTP_204_NO_CONTENT,
        )
