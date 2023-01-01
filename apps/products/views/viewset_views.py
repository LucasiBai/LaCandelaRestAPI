from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.products.filters import ProductsFilterSet, RelatedProductsFilterset
from apps.products.serializers import ProductSerializer
from apps.api_root.utils import FilterMethodsViewset


class ProductsViewSet(FilterMethodsViewset):
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
        if (
            self.action == "list"
            or self.action == "retrieve"
            or self.action == "get_related_products"
        ):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Gets products and results quantity
        """
        products = self.filter_queryset(self.get_queryset())

        if products:
            serializer = self.serializer_class(products, many=True)

            export_data = {
                "results": self.results,
                "data": serializer.data,
            }

            return Response(export_data, status=status.HTTP_200_OK)

        return Response(
            {"results": 0, "message": "Not found products."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="related-products",
        filterset_class=RelatedProductsFilterset,
    )
    def get_related_products(self, request, pk, *args, **kwargs):
        """
        Gets related products from pk
        """

        if request.method == "GET":

            try:
                int(pk)
            except:
                return Response(
                    {"message": "ID must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product = self.get_queryset().filter(pk=pk).first()

            params = request.query_params

            if params:
                related_products = self.filter_queryset(
                    self.get_queryset().filter(category=product.category).exclude(pk=pk)
                )
            else:
                related_products = (
                    self.get_queryset()
                    .filter(category=product.category)
                    .exclude(pk=pk)[:10]
                )

            if related_products:
                serializer = self.serializer_class(related_products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"message": "Not found related products"},
                status=status.HTTP_204_NO_CONTENT,
            )

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
